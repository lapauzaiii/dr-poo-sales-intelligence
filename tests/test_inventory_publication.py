"""Inventory publication regression tests; all records are synthetic test-only aggregates."""
import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from publish_inventory_snapshot import publish, should_publish

NOW = dt.datetime(2026, 10, 28, 12, tzinfo=dt.timezone.utc)


def snapshot(when="2026-10-28T10:00:00+00:00"):
    codes = [str(n) for n in range(11, 60)] + ["65"]
    rows = [
        {"county_code": code, "septic_class": kind, "count": 10}
        for code in codes for kind in ("KnownSeptic", "LikelySeptic", "SWLSeptic")
    ]
    return {
        "dataset": "florida_dep_septic_inventory_aggregates",
        "data_type": "historical_septic_inventory_not_permits",
        "source_url": "https://ags.dep.state.fl.us/arcgis/rest/services/OpenData/SEPTIC_SYSTEMS/MapServer/0",
        "retrieved_at": when,
        "county_code_mapping_verified": True,
        "county_mapping_source": "https://maps.floridahealth.gov/server/rest/services/FLWMI/FLWMI_Wastewater/MapServer/0",
        "rows": rows,
    }


class InventoryPublicationTests(unittest.TestCase):
    def test_newer_valid_snapshot_is_selected(self):
        self.assertTrue(should_publish(snapshot(), snapshot("2026-10-28T11:00:00Z"), NOW))

    def test_stale_and_equal_snapshots_are_not_selected(self):
        self.assertFalse(should_publish(snapshot(), snapshot("2026-10-28T09:00:00Z"), NOW))
        self.assertFalse(should_publish(snapshot(), snapshot("2026-10-28T10:00:00Z"), NOW))

    def test_future_clock_or_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "future"):
            should_publish(snapshot(), snapshot("2026-10-29T11:00:00Z"), NOW)
        with self.assertRaisesRegex(ValueError, "timezone"):
            should_publish(snapshot(), snapshot("2026-10-28T11:00:00"), NOW)

    def test_source_or_county_mapping_change_is_rejected(self):
        altered = snapshot("2026-10-28T11:00:00Z")
        altered["source_url"] += "/other"
        with self.assertRaisesRegex(ValueError, "source URL"):
            should_publish(snapshot(), altered, NOW)
        altered = snapshot("2026-10-28T11:00:00Z")
        altered["county_mapping_source"] = "https://example.org/other"
        with self.assertRaisesRegex(ValueError, "county mapping"):
            should_publish(snapshot(), altered, NOW)

    def test_malformed_and_duplicate_data_fail_closed(self):
        altered = snapshot("2026-10-28T11:00:00Z")
        altered["rows"].append(copy.deepcopy(altered["rows"][0]))
        with self.assertRaises(AssertionError):
            should_publish(snapshot(), altered, NOW)
        altered = snapshot("2026-10-28T11:00:00Z")
        altered["rows"][0]["count"] = -1
        with self.assertRaises(AssertionError):
            should_publish(snapshot(), altered, NOW)

    def test_file_is_unchanged_when_candidate_is_older(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            existing = path / "inventory.json"
            incoming = path / "candidate.json"
            existing.write_text(json.dumps(snapshot("2026-10-28T11:00:00Z")))
            incoming.write_text(json.dumps(snapshot("2026-10-28T10:00:00Z")))
            before = existing.read_bytes()
            self.assertFalse(publish(incoming, existing))
            self.assertEqual(existing.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
