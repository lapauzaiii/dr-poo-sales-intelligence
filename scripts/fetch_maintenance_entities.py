#!/usr/bin/env python3
"""Import only public business maintenance-entity permits from an official DEP PDF.

Never publishes phone numbers, street addresses, owners, or installation records.
The report identifies maintenance permissions, NOT installed ATUs or sales leads.
Requires pdftotext (poppler-utils); no authenticated source scraping.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPORT_URL = "https://floridadep.gov/sites/default/files/2026_0331_MEByCounty_1.pdf"
OUT = ROOT / "data" / "maintenance-entities.json"
# Permit prefix numbers in the maintenance report are *not* FL DOR CO_NO codes.
PERMIT_COUNTIES = {"10": "Clay", "16": "Duval", "55": "St. Johns"}
TERRITORY = ["Baker", "Clay", "Duval", "Nassau", "St. Johns"]
PERMIT = re.compile(r"^\s*(?P<id>\d{2}-Q[A-Z0-9]-\d{3,10})\s+(?P<name>[^\r\n]+?)\s*$")
RUN_DATE = re.compile(r"run date:\s*(\d{1,2}/\d{1,2}/\d{4})", re.I)
IGNORE = re.compile(r"^(?:\d{1,2}|\d{1,2}\s+[\w. ]+\(cont\.\)|Maintains the following advanced systems:)$", re.I)
PERSONAL = re.compile(r"\b(?:\d{3}[-.) ]+\d{3}[-. ]+\d{4}|P\.?O\.? Box|\bFL\s+\d{5})\b", re.I)

def parse_report(text: str) -> tuple[str, list[dict]]:
    date = RUN_DATE.search(text)
    if not date:
        raise ValueError("Missing official report run date")
    run_date = dt.datetime.strptime(date.group(1), "%m/%d/%Y").date().isoformat()
    records = []
    current = None
    reading_products = False

    def flush():
        nonlocal current, reading_products
        if current:
            if not current["products"]:
                raise ValueError("No product evidence for " + current["permit_id"])
            current["products"] = sorted(set(current["products"]))
            records.append(current)
        current = None
        reading_products = False

    for page_no, page in enumerate(text.split("\f"), 1):
        for raw in page.splitlines():
            line = raw.strip()
            if not line:
                continue
            m = PERMIT.match(raw)
            if m:
                flush()
                code = m.group("id")[:2]
                if code not in PERMIT_COUNTIES:
                    continue
                name = " ".join(m.group("name").split())
                if len(name) < 3 or len(name) > 150 or PERSONAL.search(name):
                    raise ValueError("Invalid business name for permit " + m.group("id"))
                current = {
                    "permit_id": m.group("id"),
                    "county": PERMIT_COUNTIES[code],
                    "entity_name": name,
                    "products": [],
                    "source_page": page_no,
                    "evidence": "official_maintenance_entity_service_permit",
                }
                continue
            if current is None:
                continue
            if line.lower().startswith("maintains the following advanced systems:"):
                reading_products = True
                continue
            if not reading_products or IGNORE.match(line):
                continue
            indent = len(raw) - len(raw.lstrip())
            # Products are indented below the narrative label. County headers,
            # page footers, business addresses and telephone numbers are not.
            if indent < 20 or PERSONAL.search(line):
                continue
            if len(line) > 95 or line.startswith("(") or re.match(r"^\d", line):
                continue
            current["products"].append(line)
    flush()
    if len(records) != len({r["permit_id"] for r in records}):
        raise ValueError("Duplicate maintenance permit identifiers")
    by_county = {c: sum(r["county"] == c for r in records) for c in TERRITORY}
    # These minimums detect layout failures, not assertions about total providers.
    if by_county["Clay"] < 2 or by_county["Duval"] < 12 or by_county["St. Johns"] < 4:
        raise ValueError("Unexpectedly sparse source extraction: " + repr(by_county))
    if any(not r["products"] for r in records):
        raise ValueError("Incomplete product extraction")
    return run_date, sorted(records, key=lambda r: (r["county"], r["permit_id"]))

def download_pdf(url: str) -> bytes:
    if url != REPORT_URL:
        raise ValueError("Only the explicitly validated official report URL is allowed")
    req = urllib.request.Request(url, headers={"User-Agent": "DrPooSalesIntelligence/1.0 (public aggregate business permit validation)"})
    with urllib.request.urlopen(req, timeout=45) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP status " + str(response.status))
        data = response.read(12_000_001)
    if not data.startswith(b"%PDF") or len(data) > 12_000_000:
        raise ValueError("Source is not a PDF or exceeds safe size limit")
    return data

def extract_pdf(pdf: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp:
        temp.write(pdf)
        temp.flush()
        result = subprocess.run(["pdftotext", "-layout", temp.name, "-"], capture_output=True, text=True, timeout=90, check=True)
    if len(result.stdout) < 10000:
        raise ValueError("Suspiciously short PDF extraction")
    return result.stdout

def build(pdf: bytes, retrieved_at: str) -> dict:
    report_date, records = parse_report(extract_pdf(pdf))
    counts = {c: sum(r["county"] == c for r in records) for c in TERRITORY}
    return {
        "dataset": "fl_dep_maintenance_entity_service_permits_by_county",
        "data_type": "maintenance_entity_permissions_not_installed_systems",
        "source_url": REPORT_URL,
        "report_date": report_date,
        "retrieved_at": retrieved_at,
        "source_sha256": hashlib.sha256(pdf).hexdigest(),
        "coverage": [{"county": c, "listed_permits": counts[c],
                      "status": "listed_in_report" if counts[c] else "not_listed_in_this_report_not_zero_installations"} for c in TERRITORY],
        "records": records,
        "privacy": "Only public business names, maintenance permit IDs, and approved product names; no addresses, phone numbers, owners or installations.",
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Local official PDF for reproducible tests")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    pdf = args.pdf.read_bytes() if args.pdf else download_pdf(REPORT_URL)
    payload = build(pdf, dt.datetime.now(dt.timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent, delete=False) as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
        temp_name = f.name
    os.replace(temp_name, args.output)
    print("Validated", len(payload["records"]), "maintenance permits:", {r["county"]: r["listed_permits"] for r in payload["coverage"]})

if __name__ == "__main__":
    main()
