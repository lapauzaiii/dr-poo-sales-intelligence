"""Synthetic parser tests only; no test business is published as a real provider."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from fetch_product_maintenance import parse_report, main

def fixture():
    lines=["Advanced System Maintenance Listing","run date: 9/15/2026",
           "      County                 City                 Maintenance Entity Company Name"]
    for product in ["Aqua-Klear","Norweco Singulair","Fuji Clean USA Fuji Clean CE"]:
        lines.append(product)
        for i in range(8):
            county=["Clay","Duval","St. Johns"][i%3]
            lines.append(f"      {county}                 Jacksonville                 Sample Provider {i} LLC")
    return "\n".join(lines)+"\f"

class ProductTests(unittest.TestCase):
    def test_product_report(self):
        date,rows=parse_report(fixture())
        self.assertEqual(date,"2026-09-15")
        self.assertEqual(len(rows),24)
        self.assertEqual(len(set(x["product"] for x in rows)),3)
        self.assertTrue(all(x["evidence"]=="official_product_sorted_maintenance_listing" for x in rows))
    def test_duplicates_deduplicated(self):
        _,rows=parse_report(fixture()+fixture())
        self.assertEqual(len(rows),24)
    def test_collector_writes_atomic_snapshot(self):
        import tempfile
        from unittest.mock import patch
        import json
        with tempfile.TemporaryDirectory() as tmp:
            pdf=Path(tmp)/"official.pdf"
            out=Path(tmp)/"products.json"
            pdf.write_bytes(b"%PDF-1.7 synthetic unit test only")
            with patch("fetch_product_maintenance.extract_pdf", return_value=fixture()), patch.object(sys,"argv",["collector","--pdf",str(pdf),"--output",str(out)]):
                main()
            data=json.loads(out.read_text())
            self.assertEqual(data["report_date"],"2026-09-15")
            self.assertEqual(len(data["records"]),24)
            self.assertTrue(data["source_sha256"])

    def test_missing_date_rejected(self):
        with self.assertRaisesRegex(ValueError,"date"):
            parse_report(fixture().replace("run date: 9/15/2026","run date: unknown"))
    def test_sparse_report_rejected(self):
        with self.assertRaisesRegex(ValueError,"sparse"):
            parse_report(fixture().replace("      Duval                 Jacksonville                 Sample Provider", "      NotOurCounty                 Jacksonville                 Sample Provider"))

if __name__=="__main__":
    unittest.main()
