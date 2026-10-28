#!/usr/bin/env python3
"""Fetch public Florida DEP septic inventory aggregates (NOT recent permit filings).

Only group counts are saved. Never persist individual points, addresses, parcel
numbers, or applicant details. County-code mapping is intentionally not assumed.
"""
import datetime
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENDPOINT = "https://ags.dep.state.fl.us/arcgis/rest/services/OpenData/SEPTIC_SYSTEMS/MapServer/0/query"
OUTPUT = ROOT / "data" / "septic-inventory-aggregate.json"

def fetch():
    params = {
        "where": "1=1",
        "outFields": "CO_NO,WW",
        "groupByFieldsForStatistics": "CO_NO,WW",
        "outStatistics": json.dumps([{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"record_count"}]),
        "returnGeometry": "false",
        "f": "json",
    }
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "DrPooSalesIntelligence/1.0 (public aggregated data)"})
    with urllib.request.urlopen(req, timeout=35) as response:
        payload = json.load(response)
    if "error" in payload:
        raise RuntimeError("ArcGIS returned an error: " + str(payload["error"]))
    features = payload.get("features")
    if not isinstance(features, list) or not features:
        raise ValueError("No grouped features returned; preserving previous snapshot")
    rows = []
    for feature in features:
        a = feature.get("attributes", {})
        county = str(a.get("CO_NO") or "").strip()
        certainty = str(a.get("WW") or "").strip()
        count = a.get("record_count")
        if not county or not certainty or not isinstance(count, int) or count < 0:
            raise ValueError("Unexpected ArcGIS grouped feature schema")
        rows.append({"county_code":county,"septic_class":certainty,"count":count})
    if len(rows) >= 2000:
        raise ValueError("ArcGIS may have truncated results; refusing incomplete snapshot")
    return {
        "dataset": "florida_dep_septic_inventory_aggregates",
        "data_type": "historical_septic_inventory_not_permits",
        "source_url": ENDPOINT.rsplit("/query",1)[0],
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "county_code_mapping_verified": False,
        "rows": sorted(rows,key=lambda x:(x["county_code"],x["septic_class"])),
    }

def main():
    data = fetch()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(data,indent=2)+"\\n")
    print("Fetched",len(data["rows"]),"county/certainty aggregates")

if __name__ == "__main__":
    main()
