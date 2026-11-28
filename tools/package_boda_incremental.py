#!/usr/bin/env python3
"""Build an overwrite-only Boda delta by comparing validated production ZIPs."""
from pathlib import Path, PurePosixPath
import argparse
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def build(source: Path, output: Path) -> None:
    subprocess.run(
        [sys.executable, str(source / "tools/package_boda.py"), "--output", str(output)],
        cwd=source, check=True,
    )


def entries(archive: zipfile.ZipFile) -> dict[str, bytes]:
    result = {}
    for info in archive.infolist():
        if info.is_dir():
            continue
        name = info.filename
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or str(path) != name or "\\" in name or name in result:
            raise SystemExit(f"Unsafe or duplicate production ZIP entry: {name}")
        result[name] = archive.read(info)
    if not result:
        raise SystemExit("Production ZIP is empty")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Git ref/SHA currently deployed on Boda")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    base = git("rev-parse", "--verify", "--end-of-options", f"{args.base}^{{commit}}")
    head = git("rev-parse", "HEAD")
    output = args.output.resolve()
    manifest_path = args.manifest.resolve() if args.manifest else None
    if manifest_path == output:
        raise SystemExit("ZIP and manifest must have different paths")
    if git("status", "--porcelain", "--untracked-files=normal"):
        raise SystemExit("Build from a clean checkout to ensure reproducible HEAD output")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    if manifest_path:
        manifest_path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="pai-boda-incremental-") as tmp:
        work = Path(tmp)
        baseline = work / "baseline"
        subprocess.run(["git", "worktree", "add", "--detach", str(baseline), base],
                       cwd=ROOT, check=True)
        try:
            build(baseline, work / "base.zip")
            build(ROOT, work / "head.zip")
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(baseline)],
                           cwd=ROOT, check=True)
        with zipfile.ZipFile(work / "base.zip") as old, zipfile.ZipFile(work / "head.zip") as new:
            before, after = entries(old), entries(new)
        removed = sorted(before.keys() - after.keys())
        if removed:
            print("Incremental deployment is not safe: public files require deletion.")
            for name in removed:
                print(f" - {name}")
            raise SystemExit(2)
        changed = sorted(name for name, data in after.items() if before.get(name) != data)
        # Prove that overlaying the delta onto the baseline exactly reproduces HEAD.
        merged = dict(before)
        merged.update({name: after[name] for name in changed})
        if merged != after:
            raise SystemExit("Incremental overlay verification failed")
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as target:
            for name in changed:
                target.writestr(name, after[name])
        with zipfile.ZipFile(output) as target:
            if target.testzip() is not None or set(target.namelist()) != set(changed):
                raise SystemExit("Incremental ZIP integrity failed")
            if any(target.read(name) != after[name] for name in changed):
                raise SystemExit("Incremental ZIP content mismatch")

    manifest = "\n".join([
        "PAI Boda incremental deployment",
        f"Base: {base}",
        f"Head: {head}",
        f"Changed public files: {len(changed)}",
        "Verified: baseline + overwrite delta equals target production artifact.",
        "",
        "Upload/overwrite these files while preserving their paths:",
        *[f"- {name}" for name in changed],
        "",
        "Do not delete other server files.",
        "",
    ])
    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(manifest, encoding="utf-8")
    print(manifest, end="")
    print(f"Incremental Boda ZIP ready: {output} ({len(changed)} file(s))")


if __name__ == "__main__":
    main()
