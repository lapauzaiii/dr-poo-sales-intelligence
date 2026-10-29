# Property-level prospecting architecture

Decision: Pursue property-level prospecting across Baker, Clay, Duval, Nassau and St. Johns counties. Do not treat septic-likelihood inventory points as verified conventional installations.

## Data acquisition gates
- Start with Florida DEP FLWMI and county/health department permit exports; record exact source URL, agency, retrieval time, license/terms and approved use.
- Obtain explicit confirmation of bulk access and commercial reuse where terms are unclear. Do not bypass rate limits, authentication or robots restrictions.
- No property-level export may be committed to this public repository or included in static Pages artifacts.
- Before ingestion, validate fields, county mapping, provenance, duplicate handling, stale records, and suppression/opt-out requirements.

## Private storage design (proposed, not provisioned)
Use an authenticated backend and private database within the existing Cloudflare account only after checking cost, access controls and preview-domain isolation. No paid services without approval.

Entities:
- source_registry: source_id, agency, URL, rights_status, retrieved_at, source_date, checksum, schema_version.
- property: internal_id, county, normalized parcel key, location fields, source_id, verification_status.
- septic_evidence: evidence_id, property_id, permit_reference, category, status, issued_at, observed_at, source_id, confidence, reviewer.
- prospect: prospect_id, property_id, eligibility_basis, priority, workflow_status, reviewed_at.
- outreach_suppression: internal property key, suppression reason, recorded_at.

## Rules
- KnownSeptic is a wastewater-likelihood classification, not proof of conventional type, ownership, active permit, pumping interval, or sales availability.
- Keep source assertions separate from inferred propensity scores. Every displayed claim links to evidence.
- Do not store owner names, personal phones, emails, or other unnecessary identifiers by default.
- Prospects may be candidates with uncertainty clearly labeled; verified system labels require official installation-level evidence.
- Require authorized users, role-scoped access, audit history, data retention policy, and suppression checks before outreach.
- No automatic messages, contact enrichment, or bulk outreach in alpha.

## Implementation sequence
1. Verify source rights and access for parcel-level records.
2. Implement schema and fixture-only tests for provenance, classification, deduplication and suppression.
3. Verify private backend authentication, preview isolation and cost ceiling.
4. Ingest an approved bounded sample, review matching accuracy, then expand county by county.
5. Add protected property search, evidence detail and manual qualification queue.
6. Publish release notes with data counts, freshness, quality checks, deployment commit and blockers.

## Current blocker
No validated rights or authorized bulk property-level permit export, protected database, or confirmed team access. Keep all existing live property-level feeds empty until these gates are met.
