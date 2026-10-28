"""Synthetic unit-test input only. Never publish test fixtures as permit data."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_maintenance_entities import parse_report

def sample():
    lines = ["Active Maintenance Entity Service Permits by County", "run date: 3/31/2026"]
    for prefix, code, n in [("10", "QC", 2), ("16", "QJ", 12), ("55", "QS", 4)]:
        for i in range(n):
            lines += [
                f"                  {prefix}-{code}-{i+1000000} Sample Business {i} LLC",
                "                                  (904) 555-9999",
                "                                  123 Example Street",
                "                                  Jacksonville, FL 32201",
                "                                  Maintains the following advanced systems:",
                "                                      Fuji Clean USA Fuji Clean CEN",
                "                                      Norweco Singulair",
            ]
    return "\n".join(lines) + "\f"

class ParserTests(unittest.TestCase):
    def test_maintenance_permissions_without_personal_data(self):
        date, records = parse_report(sample())
        self.assertEqual(date, "2026-03-31")
        self.assertEqual(len(records), 18)
        self.assertEqual(records[0]["county"], "Clay")
        self.assertEqual(records[-1]["county"], "St. Johns")
        for row in records:
            self.assertEqual(row["products"], ["Fuji Clean USA Fuji Clean CEN", "Norweco Singulair"])
            self.assertNotIn("555", repr(row))
            self.assertNotIn("Example Street", repr(row))
            self.assertEqual(row["evidence"], "official_maintenance_entity_service_permit")

    def test_duplicate_permit_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            parse_report(sample() + sample())

    def test_missing_date_rejected(self):
        with self.assertRaisesRegex(ValueError, "run date"):
            parse_report(sample().replace("run date: 3/31/2026", "run date: missing"))

    def test_missing_product_rejected(self):
        with self.assertRaisesRegex(ValueError, "No product"):
            parse_report(sample().replace("                                      Norweco Singulair", "").replace("                                      Fuji Clean USA Fuji Clean CEN", ""))

    def test_non_territory_permits_not_included(self):
        _, rows = parse_report(sample() + "                  09-QL-1234567 Outside LLC\n                                  Maintains the following advanced systems:\n                                      Hoot\n")
        self.assertEqual(len(rows), 18)

if __name__ == "__main__":
    unittest.main()
