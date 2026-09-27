#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "site.json"


def load_config_document() -> dict:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    environments = data.get("environments") or {}
    if not isinstance(environments, dict) or not environments:
        raise SystemExit("config/site.json: environments must be a non-empty object")

    seen_bases = set()
    for name, raw in environments.items():
        if not isinstance(raw, dict):
            raise SystemExit(f"config/site.json: environment {name!r} must be an object")

        base_url = raw.get("base_url")
        if not isinstance(base_url, str):
            raise SystemExit(f"config/site.json: environment {name!r} base_url must be a string")
        base_url = base_url.strip()
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.netloc or not base_url.endswith("/"):
            raise SystemExit(f"config/site.json: environment {name!r} base_url must be an https URL ending with /")
        if base_url in seen_bases:
            raise SystemExit(f"config/site.json: duplicate base_url {base_url!r}")
        seen_bases.add(base_url)

        if not isinstance(raw.get("allow_indexing"), bool):
            raise SystemExit(f"config/site.json: environment {name!r} allow_indexing must be boolean")

        custom_domain = raw.get("custom_domain")
        if custom_domain is not None:
            if not isinstance(custom_domain, str) or not custom_domain.strip():
                raise SystemExit(f"config/site.json: environment {name!r} custom_domain must be a non-empty string or null")
            if "://" in custom_domain or "/" in custom_domain:
                raise SystemExit(f"config/site.json: environment {name!r} custom_domain must be a hostname only")
            if parsed.hostname != custom_domain.strip():
                raise SystemExit(f"config/site.json: environment {name!r} custom_domain must match base_url hostname")

    active = data.get("active_environment")
    if active not in environments:
        raise SystemExit(f"config/site.json: unknown active_environment {active!r}")
    return data


def load_site_config() -> dict:
    data = CONFIG
    active = data["active_environment"]
    env = dict(data["environments"][active])
    env["name"] = active
    env["base_url"] = env["base_url"].strip()
    custom_domain = env.get("custom_domain")
    env["custom_domain"] = custom_domain.strip() if custom_domain else None
    return env


CONFIG = load_config_document()
SITE = load_site_config()
BASE_URL = SITE["base_url"]
CUSTOM_DOMAIN = SITE["custom_domain"]
ALLOW_INDEXING = SITE["allow_indexing"]
ENVIRONMENT = SITE["name"]
KNOWN_BASE_URLS = frozenset(env["base_url"].strip() for env in CONFIG["environments"].values())
