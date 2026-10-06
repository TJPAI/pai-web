#!/usr/bin/env python3
"""Build a minimal Boda deployment ZIP from changes since a deployed Git ref.

The script always builds the canonical production artifact first, then selects only
files whose deployed output is affected by the source diff. If a change cannot be
mapped safely to a small set of public files, it fails with a clear instruction to
use the full Boda package instead.
"""
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

BUNDLED_CSS_SOURCES = {
    "assets/css/refine.css",
    "assets/css/refine-base.css",
    "assets/css/app-core.css",
    "assets/css/typography.css",
    "assets/css/desktop-layout.css",
}
DIRECT_PUBLIC_FILES = {"robots.txt", "sitemap.xml", "site.json", "sw.js"}
IGNORED_PREFIXES = (".github/",)
IGNORED_FILES = {
    ".gitignore",
    "README.md",
    "MAINTENANCE.md",
    "PRODUCTION_CUTOVER.md",
    "STABLE_BASELINE.md",
}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout


def classify(base: str) -> tuple[list[str], list[str]]:
    rows = git("diff", "--name-status", "--find-renames", f"{base}...HEAD").splitlines()
    deploy: set[str] = set()
    unsafe: list[str] = []

    for row in rows:
        if not row.strip():
            continue
        parts = row.split("\t")
        status = parts[0]
        paths = parts[1:]

        if status.startswith("D") or status.startswith("R"):
            unsafe.append(row)
            continue

        path = paths[-1]
        if path in IGNORED_FILES or path.startswith(IGNORED_PREFIXES):
            continue

        if path in BUNDLED_CSS_SOURCES:
            deploy.add("assets/css/refine-bundle.css")
        elif path.startswith("assets/css/"):
            deploy.add(path)
        elif path.startswith(("assets/js/", "assets/images/", "assets/icons/")):
            deploy.add(path)
        elif path.endswith(".html") and not path.startswith(("templates/", "geosketch-mvp/")):
            deploy.add(path)
        elif path in DIRECT_PUBLIC_FILES:
            deploy.add(path)
        elif path in {"data/publications.json", "data/publications-archive.json"}:
            deploy.update({"publications.html", "en/publications.html"})
        elif path.startswith(("tools/", "config/", "templates/", "data/")):
            unsafe.append(row)
        elif path.startswith("geosketch-mvp/"):
            continue
        else:
            unsafe.append(row)

    return sorted(deploy), unsafe


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base", required=True, help="Git ref/SHA currently deployed on Boda")
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--manifest", type=Path)
args = parser.parse_args()

# Fail early if the reference does not exist locally.
subprocess.run(["git", "rev-parse", "--verify", f"{args.base}^{{commit}}"], cwd=ROOT, check=True,
               stdout=subprocess.DEVNULL)

deploy_files, unsafe_changes = classify(args.base)
if unsafe_changes:
    print("Incremental deployment is not safe for this change set. Use the full Boda ZIP.")
    print("Changes requiring a full deployment:")
    for item in unsafe_changes:
        print(f" - {item}")
    raise SystemExit(2)

if not deploy_files:
    print("No public Boda files changed; no incremental package is needed.")
    raise SystemExit(0)

args.output = args.output.resolve()
args.output.parent.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory(prefix="pai-boda-incremental-") as tmp:
    full_zip = Path(tmp) / "full.zip"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "package_boda.py"), "--output", str(full_zip)],
        cwd=ROOT,
        check=True,
    )

    with zipfile.ZipFile(full_zip) as source:
        available = set(source.namelist())
        missing = [path for path in deploy_files if path not in available]
        if missing:
            raise SystemExit(f"Incremental artifact mapping missing deployed file(s): {missing}")

        with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as target:
            for path in deploy_files:
                target.writestr(path, source.read(path))

with zipfile.ZipFile(args.output) as archive:
    bad = archive.testzip()
    if bad is not None:
        raise SystemExit(f"Incremental ZIP integrity failed at {bad}")

head = git("rev-parse", "HEAD").strip()
base_resolved = git("rev-parse", args.base).strip()
manifest = [
    "PAI Boda incremental deployment",
    f"Base: {base_resolved}",
    f"Head: {head}",
    "",
    "Upload/overwrite these files while preserving their paths:",
    *[f"- {path}" for path in deploy_files],
    "",
    "Do not delete other server files.",
]
manifest_text = "\n".join(manifest) + "\n"
if args.manifest:
    args.manifest = args.manifest.resolve()
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(manifest_text, encoding="utf-8")

print(manifest_text, end="")
print(f"Incremental Boda ZIP ready: {args.output} ({len(deploy_files)} file(s))")
