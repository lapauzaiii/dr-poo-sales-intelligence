"""Guard against conflating DOR septic inventory codes with permit jurisdictions."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class CountyCodeTests(unittest.TestCase):
    def test_independent_official_code_systems(self):
        d=json.loads((ROOT/"data/county-and-equipment-validation.json").read_text())
        self.assertEqual(d["counties"],{"12":"Baker","20":"Clay","26":"Duval","55":"Nassau","65":"St. Johns"})
        self.assertEqual(d["maintenance_permit_prefixes"],{"10-QC":"Clay","16-QJ":"Duval","55-QS":"St. Johns"})
        self.assertNotEqual(d["counties"]["55"],d["maintenance_permit_prefixes"]["55-QS"])
        self.assertIn("different code systems",d["important_distinction"])
    def test_no_inferred_installed_units(self):
        for name in ["atu-pbts-systems.json","opportunities.json"]:
            d=json.loads((ROOT/"data"/name).read_text())
            self.assertEqual(d["records"],[])
            self.assertEqual(d["source_status"],"no_verified_records_available")

if __name__=="__main__":
    unittest.main()
