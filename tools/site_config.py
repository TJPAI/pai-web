#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "site.json"


def load_site_config() -> dict:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    active = data.get("active_environment")
    environments = data.get("environments") or {}
    if active not in environments:
        raise SystemExit(f"config/site.json: unknown active_environment {active!r}")
    env = dict(environments[active])
    base_url = str(env.get("base_url") or "").strip()
    if not base_url.startswith("https://") or not base_url.endswith("/"):
        raise SystemExit("config/site.json: active base_url must be an https URL ending with /")
    env["name"] = active
    env["base_url"] = base_url
    env["allow_indexing"] = bool(env.get("allow_indexing"))
    custom_domain = env.get("custom_domain")
    env["custom_domain"] = str(custom_domain).strip() if custom_domain else None
    return env


SITE = load_site_config()
BASE_URL = SITE["base_url"]
CUSTOM_DOMAIN = SITE["custom_domain"]
ALLOW_INDEXING = SITE["allow_indexing"]
ENVIRONMENT = SITE["name"]
