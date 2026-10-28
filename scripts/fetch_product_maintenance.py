#!/usr/bin/env python3
"""Extract recent product-sorted public maintenance-provider listings from DEP.

This September report contains no service-permit IDs. Do not join its business
names to March permit IDs without independent identity resolution.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import urllib.request
from fetch_maintenance_entities import extract_pdf

ROOT = Path(__file__).resolve().parents[1]
URL = "https://floridadep.gov/sites/default/files/2026_0924_MEByProduct.pdf"
OUTPUT = ROOT / "data" / "maintenance-products.json"
COUNTIES = ["Baker", "Clay", "Duval", "Nassau", "St. Johns"]
RUN = re.compile(r"run date:\s*(\d{1,2}/\d{1,2}/\d{4})", re.I)
ROW = re.compile(r"^\s*(Baker|Clay|Duval|Nassau|St\. Johns)\s{2,}(.+?)\s{2,}(.+?)\s*$")
SENSITIVE = re.compile(r"\b\d{3}[-.) ]+\d{3}[-. ]+\d{4}\b|@|\b\d{5}(?:-\d{4})?\b", re.I)

def parse_report(text):
    m = RUN.search(text)
    if not m:
        raise ValueError("Missing product report date")
    report_date = dt.datetime.strptime(m.group(1), "%m/%d/%Y").date().isoformat()
    current_product = None
    started = False
    records = []
    for page_no, page in enumerate(text.split("\f"), 1):
        for raw in page.splitlines():
            line = raw.strip()
            if not line:
                continue
            if "Maintenance Entity Company Name" in line and "County" in line:
                started = True
                continue
            if not started:
                continue
            m = ROW.match(raw)
            if m:
                if not current_product:
                    raise ValueError("Territory row has no product heading: " + line)
                county, city, company = m.groups()
                city, company = " ".join(city.split()), " ".join(company.split())
                if not city or not company or SENSITIVE.search(city+" "+company):
                    raise ValueError("Invalid business row: " + line)
                records.append({"county": county, "city": city, "entity_name": company,
                                "product": current_product, "source_page": page_no,
                                "evidence": "official_product_sorted_maintenance_listing"})
                continue
            # Product headings are flush left. Table rows begin further right.
            indent = len(raw) - len(raw.lstrip())
            if indent > 2:
                continue
            if line in {"County", "City"} or line.isdigit() or "381.0065" in line:
                continue
            if line.startswith(("Advanced System", "Florida Permitted", "Under these", "A person", "personally")):
                continue
            heading = re.sub(r"\s*\(cont\.\)\s*$", "", line, flags=re.I).strip()
            if 2 <= len(heading) <= 90 and not SENSITIVE.search(heading):
                current_product = heading
    if len(records) < 20:
        raise ValueError("Unexpectedly sparse product report extraction: " + str(len(records)))
    if len({r["product"] for r in records}) < 3:
        raise ValueError("Product headings not extracted")
    keys = set()
    deduped = []
    for r in records:
        key = (r["county"], r["entity_name"].casefold(), r["product"].casefold(), r["city"].casefold())
        if key not in keys:
            keys.add(key)
            deduped.append(r)
    return report_date, sorted(deduped, key=lambda r:(r["county"],r["product"],r["entity_name"]))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",type=Path)
    p.add_argument("--output",type=Path,default=OUTPUT)
    args=p.parse_args()
    if args.pdf:
        pdf=args.pdf.read_bytes()
    else:
        req=urllib.request.Request(URL,headers={"User-Agent":"DrPooSalesIntelligence/1.0 (public official report)"})
        with urllib.request.urlopen(req,timeout=45) as response:
            pdf=response.read(12_000_001)
    if not pdf.startswith(b"%PDF") or len(pdf)>12_000_000:
        raise ValueError("Invalid or oversized official product report")
    report_date,records=parse_report(extract_pdf(pdf))
    out={"dataset":"fl_dep_maintenance_entities_by_product","data_type":"product_sorted_maintenance_permissions_not_installations",
         "source_status":"verified_report_extraction","source_url":URL,"report_date":report_date,
         "retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),"source_sha256":hashlib.sha256(pdf).hexdigest(),
         "coverage":[{"county":c,"listing_rows":sum(r["county"]==c for r in records),
                      "status":"listed_in_report" if any(r["county"]==c for r in records) else "not_listed_in_report"} for c in COUNTIES],
         "records":records,"notes":"Product-sorted provider listing, no maintenance permit IDs. Business names are not deduplicated across permit jurisdictions and must not be used as installed-system evidence."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    import os,tempfile
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.output.parent,delete=False) as f:
        json.dump(out,f,indent=2,ensure_ascii=False);f.write("\n");temp=f.name
    os.replace(temp,args.output)
    print("Validated",len(records),"product/provider listing rows from",report_date)

if __name__=="__main__":
    main()
