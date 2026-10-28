#!/usr/bin/env python3
"""Validate public alpha artifacts before deployment or publishing refreshed data."""
import datetime as dt
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COUNTIES = {"12": "Baker", "20": "Clay", "26": "Duval", "55": "Nassau", "65": "St. Johns"}
TERRITORY = set(COUNTIES.values())
MAINTENANCE_PREFIX = {"10": "Clay", "16": "Duval", "55": "St. Johns"}
PRIVATE = re.compile(r"(?:\b\d{3}[-.) ]+\d{3}[-. ]+\d{4}\b|@|\b(?:street|drive|avenue|road)\b)", re.I)

def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))

def iso(value):
    if not isinstance(value, str):
        raise ValueError("Expected ISO timestamp")
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))

def validate_inventory(d):
    assert d["data_type"] == "historical_septic_inventory_not_permits"
    assert d["source_url"].startswith("https://ags.dep.state.fl.us/")
    iso(d["retrieved_at"])
    assert d.get("county_code_mapping_verified") is True, "Official DOR domain verified; update collector metadata"
    assert len(d["rows"]) >= 150
    keys = set()
    for r in d["rows"]:
        assert r["county_code"] in {str(n) for n in range(11, 78)}
        assert r["septic_class"] in ("KnownSeptic", "LikelySeptic", "SWLSeptic")
        assert type(r["count"]) is int and r["count"] >= 0
        key = (r["county_code"], r["septic_class"])
        assert key not in keys, "Duplicate county/class"
        keys.add(key)
    assert set(COUNTIES).issubset({r["county_code"] for r in d["rows"]})

def validate_maintenance(d):
    assert d["data_type"] == "maintenance_entity_permissions_not_installed_systems"
    assert d["source_url"].startswith("https://floridadep.gov/sites/default/files/")
    assert [r["county"] for r in d["coverage"]] == ["Baker", "Clay", "Duval", "Nassau", "St. Johns"]
    records = d["records"]
    if d.get("source_status") == "pending_initial_ingestion":
        assert not records
        return
    iso(d["retrieved_at"])
    dt.date.fromisoformat(d["report_date"])
    assert re.fullmatch(r"[a-f0-9]{64}", d["source_sha256"])
    assert len(records) >= 18
    ids = set()
    for r in records:
        pid = r["permit_id"]
        assert re.fullmatch(r"\d{2}-Q[A-Z0-9]-\d{3,10}", pid)
        assert MAINTENANCE_PREFIX[pid[:2]] == r["county"]
        assert pid not in ids
        ids.add(pid)
        assert 3 <= len(r["entity_name"]) <= 150
        assert not PRIVATE.search(r["entity_name"])
        assert 1 <= len(r["products"]) <= 30
        assert len(r["products"]) == len(set(r["products"]))
        assert all(isinstance(p, str) and 1 <= len(p) <= 95 and not PRIVATE.search(p) for p in r["products"])
        assert type(r["source_page"]) is int and r["source_page"] > 0
        assert r["evidence"] == "official_maintenance_entity_service_permit"
    for c in d["coverage"]:
        assert c["listed_permits"] == sum(r["county"] == c["county"] for r in records)

def validate_products(d):
    assert d["data_type"] == "product_sorted_maintenance_permissions_not_installations"
    assert d["source_url"].startswith("https://floridadep.gov/sites/default/files/")
    assert [x["county"] for x in d["coverage"]] == ["Baker", "Clay", "Duval", "Nassau", "St. Johns"]
    records = d["records"]
    if d.get("source_status") == "pending_initial_ingestion":
        assert not records
        return
    assert d["source_status"] == "verified_report_extraction"
    iso(d["retrieved_at"])
    dt.date.fromisoformat(d["report_date"])
    assert re.fullmatch(r"[a-f0-9]{64}", d["source_sha256"])
    assert len(records) >= 20
    keys = set()
    for r in records:
        assert r["county"] in TERRITORY
        assert 2 <= len(r["city"]) <= 100 and not PRIVATE.search(r["city"])
        assert 3 <= len(r["entity_name"]) <= 150 and not PRIVATE.search(r["entity_name"])
        assert 2 <= len(r["product"]) <= 95 and not PRIVATE.search(r["product"])
        assert type(r["source_page"]) is int and r["source_page"] > 0
        assert r["evidence"] == "official_product_sorted_maintenance_listing"
        key = (r["county"], r["city"].casefold(), r["entity_name"].casefold(), r["product"].casefold())
        assert key not in keys
        keys.add(key)
    for c in d["coverage"]:
        assert c["listing_rows"] == sum(r["county"] == c["county"] for r in records)

def validate_empty_evidence(d, kind):
    assert d["data_type"] == kind
    assert d["records"] == [], "Evidence-backed records require a separate authorized ingestion review"
    assert d["source_status"] == "no_verified_records_available"

def main():
    validate_inventory(load("septic-inventory-aggregate.json"))
    validate_maintenance(load("maintenance-entities.json"))
    validate_products(load("maintenance-products.json"))
    validate_empty_evidence(load("atu-pbts-systems.json"), "verified_atu_pbts_installations")
    validate_empty_evidence(load("opportunities.json"), "evidence_backed_opportunities")
    print("PASS: inventory, county and product maintenance permissions, empty verified systems and opportunities")

if __name__ == "__main__":
    main()
