# Permit intelligence MVP
## Scope
Duval, Clay, St. Johns, Nassau and Baker. Both competitor permit attribution and modeled revenue opportunity.
## Current implementation
- `prototype/intelligence.html`: responsive competitor activity, permit table, filters, synthetic rate-based ROI scenario.
- `data/permit-intelligence.json`: 36 fabricated permit records. Explicit synthetic provenance.
- `scripts/permit_pipeline.py`: normalization of an **explicitly supplied, authorized** JSON export. No uncontrolled scraping.
- `.github/workflows/permit-intelligence.yml`: daily scheduled validation (12:17 UTC). **It does not retrieve live permits until a legally accessible, documented source is configured.**
## Source onboarding
For each county identify official export/API, permitted automation frequency, available contractor/permit/status fields, pagination, and update semantics. Normalize and deduplicate permit numbers; preserve evidence links and retrieval timestamps. Never confuse permit counts with actual completed jobs or routine pumping volume.
## Public site policy
Only publish limited, non-personal permit metadata where allowed; no names of owners, property addresses, phone numbers, customer notes, CRM credentials, or sales dispositions. Verify source licensing and privacy rules before enabling production publication.
## ROI definition
Modeled market value = sum of synthetic rate for each permit type. Potential captured revenue = modeled value × actionable share × capture rate. Scenario ROI = (potential captured revenue × contribution margin − campaign spend) / campaign spend. A competitor-associated permit is not necessarily actionable.
## Future
Replace synthetic rates with verified published Dr. Poo rate card (URL not yet supplied). Confirm source feeds and then implement automatic retrieval with integration tests, coverage reporting, and alerts on failed refreshes. No database or Jobber integration in this phase.
