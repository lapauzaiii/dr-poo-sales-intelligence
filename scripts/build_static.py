#!/usr/bin/env python3
"""Publish only the evidence-only static alpha, not repository source or tests."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
PAGES = ["index.html", "prototype/index.html", "prototype/intelligence.html",
         "prototype/inventory.html", "prototype/atu-pbts.html", "prototype/executive.html"]
DATA = ["data/septic-inventory-aggregate.json", "data/maintenance-entities.json",
        "data/maintenance-products.json", "data/atu-pbts-systems.json", "data/opportunities.json", "data/contractor-permit-discovery.json"]
ALLOW = PAGES + DATA

def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    for rel in ALLOW:
        src = ROOT / rel
        if not src.is_file():
            raise FileNotFoundError("Required production artifact missing: " + rel)
        if rel.endswith(".json"):
            json.loads(src.read_text(encoding="utf-8"))
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    (OUT / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Frame-Options: DENY\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n", encoding="utf-8")
    deployed = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()}
    expected = set(ALLOW) | {"_headers"}
    if deployed != expected:
        raise AssertionError("Unexpected files in production bundle: " + repr(deployed ^ expected))
    print("PASS: isolated static production bundle with", len(deployed), "allowlisted files")

if __name__ == "__main__":
    build()
