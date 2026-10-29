#!/usr/bin/env python3
"""Static safety checks for private prospecting API and migration."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
api=(root/"functions/api/properties.js").read_text()
migration=(root/"migrations/0001_property_intelligence.sql").read_text()
build=(root/"scripts/build_static.py").read_text()
assert 'crypto.subtle.verify' in api
assert 'Cf-Access-Jwt-Assertion' in api
assert "rights_status='approved'" in api
assert "e.review_status='verified'" in api
assert 'outreach_suppression' in api
assert 'address_line' not in api and 'parcel_key' not in api
assert 'ACCESS_AUD' in api and 'ACCESS_TEAM_DOMAIN' in api and 'PROPERTY_DB' in api
for name in ('source_registry','properties','septic_evidence','service_history','prospects','outreach_suppression'):
    assert 'CREATE TABLE IF NOT EXISTS '+name in migration
assert 'functions/' not in build and 'migrations/' not in build
print("PASS: private API access gates, evidence requirements and public bundle isolation")
