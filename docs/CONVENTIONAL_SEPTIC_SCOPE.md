# Conventional septic intelligence: source and eligibility contract

This module is an extension of the existing DEP inventory dashboard, not a list of verified conventional installations.

## Current evidence
- Official FLWMI ArcGIS wastewater-method inventory: https://ags.dep.state.fl.us/arcgis/rest/services/OpenData/SEPTIC_SYSTEMS/MapServer/0
- Existing validated five-county grouped snapshot: `data/septic-inventory-aggregate.json`
- County DOR codes: Baker 12, Clay 20, Duval 26, Nassau 55, St. Johns 65.

## Classification rules
1. `KnownSeptic` means higher-confidence septic wastewater classification, **not** proof of a conventional system.
2. `LikelySeptic` and other likelihood categories are unverified predictions.
3. Do not classify any record as conventional, ATU, PBTS, active, pump-due, or a sales opportunity without a separate authoritative permit or inspection record supporting that exact claim.
4. Never infer service dates from installation age, aggregate counts, or county averages.
5. Never join inventory county codes to maintenance permit jurisdiction prefixes.

## Future property-level evidence contract
A candidate may be promoted to `verified_conventional` only when an authorized source identifies a specific permitted installation and conventional system type. Required non-personal metadata: source agency, source URL or official document identifier, permit identifier (stored only in approved private storage), source publication/record date, retrieval timestamp, system category, classification method, and validation status. Retain evidence for each claim. Conflicting, revoked, missing, or stale evidence must be marked for review rather than silently resolved.

## Privacy and rights
Do not commit parcel identifiers, addresses, owner names, phone numbers, personal information, or raw permit exports to this public repository. Confirm publication and commercial-reuse rights before property-level collection. Protect any approved private storage and verify Cloudflare Access coverage, including previews, before exposing such data.

## Proposed dashboard
Reuse the validated inventory aggregate for county filters, known/likely/other counts, source dates and provenance. Label the view `Conventional septic market exploration`, not `verified conventional systems`. Provide source-health warnings and explicitly show zero verified conventional installations until permitted evidence exists.

## Acceptance tests
- Reject malformed/negative inventory counts and unsupported county codes.
- Verify category mapping never promotes `KnownSeptic` to `verified_conventional`.
- Reject opportunity creation without installation-level evidence.
- Verify the production allowlist contains no parcel or personal data.
- Verify failed refreshes retain the last validated snapshot.

## Blockers
Official property-level conventional permit export, terms of reuse, permitted identifiers and retention policy are not yet confirmed. Until then, continue using aggregate data only. No paid service required.
