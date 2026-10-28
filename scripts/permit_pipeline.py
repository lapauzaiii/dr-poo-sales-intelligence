#!/usr/bin/env python3
"""Safe permit feed normalizer. Default mode is synthetic fixture; optional authorized JSON export.
Never scrapes undocumented county portals. Never publishes applicant, owner, or address details.
"""
import argparse, datetime, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
COUNTIES={"duval":"Duval","clay":"Clay","st. johns":"St. Johns","nassau":"Nassau","baker":"Baker"}
TYPES={"installation","repair","replacement","inspection"}
def normalize(row):
    county=COUNTIES.get(str(row.get("county","")).strip().lower())
    kind=str(row.get("type","")).strip().lower()
    if not county or kind not in TYPES:return None
    permit=str(row.get("permit_number","")).strip()
    if not permit or len(permit)>100:return None
    filed=str(row.get("filed_at","")).strip()
    try:datetime.date.fromisoformat(filed)
    except ValueError:return None
    contractor=re.sub(r"\\s+"," ",str(row.get("contractor") or "Unspecified")).strip()[:120]
    return {"id":permit,"county":county,"type":kind,"contractor":contractor,"status":str(row.get("status") or "Unknown")[:40],"filed_at":filed,"source":"authorized_export","source_url":str(row.get("source_url") or "")[:500]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=pathlib.Path,help="Locally provided authorized JSON array with permit_number, county, type, filed_at, contractor, status, source_url")
    p.add_argument("--output",type=pathlib.Path,default=ROOT/"data"/"permit-intelligence.json")
    args=p.parse_args()
    if not args.input:
        print("No authorized permit export configured. Retaining synthetic fixture without changes.")
        return
    rows=json.loads(args.input.read_text())
    if not isinstance(rows,list):raise ValueError("Input must be a JSON array")
    cleaned={(r["county"],r["id"]):r for item in rows if isinstance(item,dict) if (r:=normalize(item))}
    if rows and not cleaned:raise ValueError("No valid permits in supplied export; refusing to replace dashboard data")
    if any(not r["source_url"].startswith("https://") for r in cleaned.values()):raise ValueError("Every imported record must include a verifiable HTTPS source URL")
    existing=json.loads((ROOT/"data"/"permit-intelligence.json").read_text())
    out={"mode":"verified_permit_export","generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source_status":"authorized_export","source_notes":"Permit records normalized from explicitly supplied authorized export. Only limited non-personal fields published.","rates":existing["rates"],"published_rate_card":existing.get("published_rate_card"),"pricing_source":existing.get("pricing_source"),"pricing_verified_on":existing.get("pricing_verified_on"),"permits":sorted(cleaned.values(),key=lambda r:r["filed_at"],reverse=True)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n")
    print("Normalized",len(cleaned),"records")
if __name__=="__main__":main()
