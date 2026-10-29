-- Phase 1 inspection event ledger. Private D1 only; no property records in GitHub.
CREATE TABLE IF NOT EXISTS inspection_events (
 inspection_id TEXT PRIMARY KEY,
 property_id TEXT REFERENCES properties(property_id),
 evidence_id TEXT REFERENCES septic_evidence(evidence_id),
 source_id TEXT NOT NULL REFERENCES source_registry(source_id),
 permit_reference TEXT,
 county TEXT NOT NULL CHECK(county IN ('Baker','Clay','Duval','Nassau','St. Johns')),
 stage TEXT NOT NULL CHECK(stage IN ('site_evaluation','pre_install','construction','final_review','reinspection','operating','other','unknown')),
 outcome TEXT NOT NULL DEFAULT 'unknown' CHECK(outcome IN ('approved','disapproved','pending','cancelled','unknown')),
 inspected_at TEXT,
 inspector_type TEXT CHECK(inspector_type IN ('agency','private_provider','contractor','unknown') OR inspector_type IS NULL),
 contractor_registration TEXT,
 source_document_url TEXT,
 source_record_id TEXT,
 notes TEXT,
 review_status TEXT NOT NULL DEFAULT 'pending' CHECK(review_status IN ('pending','verified','rejected','conflicted')),
 observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 reviewed_at TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK(property_id IS NOT NULL OR permit_reference IS NOT NULL OR source_record_id IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS idx_inspections_county_stage ON inspection_events(county,stage,outcome);
CREATE INDEX IF NOT EXISTS idx_inspections_permit ON inspection_events(county,permit_reference);
CREATE INDEX IF NOT EXISTS idx_inspections_property ON inspection_events(property_id,inspected_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_inspections_source_record ON inspection_events(source_id,source_record_id) WHERE source_record_id IS NOT NULL;
