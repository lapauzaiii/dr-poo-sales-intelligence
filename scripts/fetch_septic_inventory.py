#!/usr/bin/env python3
"""Fetch public Florida DEP septic inventory aggregates (NOT recent permit filings).

Only group counts are saved. Never persist individual points, addresses, parcel
numbers, or applicant details. CO_NO uses Florida DOR county codes, verified against the DOH FLWMI ArcGIS coded-value domain.
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
        if not isinstance(a, dict):
            raise ValueError("ArcGIS feature attributes must be an object")
        fields = {str(key).casefold(): value for key, value in a.items()}
        if not {"co_no", "ww", "record_count"}.issubset(fields):
            raise ValueError("ArcGIS missing expected fields: " + repr(a))
        county = str(fields["co_no"]).strip() if fields["co_no"] is not None else None
        certainty = str(fields["ww"]).strip() if fields["ww"] is not None else None
        count = fields["record_count"]
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("ArcGIS invalid aggregate count: " + repr(a))
        rows.append({"county_code":county or None,"septic_class":certainty or None,"count":count})
    if len(rows) >= 2000:
        raise ValueError("ArcGIS may have truncated results; refusing incomplete snapshot")
    return {
        "dataset": "florida_dep_septic_inventory_aggregates",
        "data_type": "historical_septic_inventory_not_permits",
        "source_url": ENDPOINT.rsplit("/query",1)[0],
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "county_code_mapping_verified": True,\n        "county_code_system": "Florida Department of Revenue (CO_NO)",\n        "county_mapping_source": "https://maps.floridahealth.gov/server/rest/services/FLWMI/FLWMI_Wastewater/MapServer/0",
        "rows": sorted(rows,key=lambda x:(x["county_code"] or "",x["septic_class"] or "")),
    }

def main():
    data = fetch()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + chr(10), encoding="utf-8")
    print("Fetched",len(data["rows"]),"county/certainty aggregates")

if __name__ == "__main__":
    main()
