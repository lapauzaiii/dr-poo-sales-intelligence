# Property septic system type and sizing data contract

Goal: represent installed septic equipment specifications with source-level evidence, without inventing measurements or equating permit design with as-built installation.

## Field definitions
- system_category: conventional_gravity | conventional_pressure | mound | drip | ATU | PBTS | other | unknown
- tank_capacity_gallons: positive integer or null; distinguish total versus per-tank
- tank_count: positive integer or null
- tank_material: concrete | fiberglass | polyethylene | other | unknown
- design_flow_gpd: positive number or null
- drainfield_type: trench | chamber | bed | drip | mound | other | unknown
- drainfield_area_sqft: positive number or null
- manufacturer, model, rated_treatment_capacity_gpd: optional for advanced systems
- installation_date, final_inspection_date, last_verified_service_date: independent nullable dates
- configuration_status: proposed | permitted | as_built | inspected | field_verified | unknown

## Evidence required for each populated value
Record source agency, source document/permit reference, document date, retrieval date, rights status, extraction method, reviewer, and a field-specific citation (page or drawing reference). Do not copy personal identifiers into public artifacts. Record conflicting values rather than overwriting them.

## Rules
- Inventory `KnownSeptic` does not establish system type, capacity, installation date, or service need.
- Design flow (gallons/day) is not tank volume (gallons); do not convert between them.
- Permit-approved equipment is not automatically verified as installed. Preserve proposed, permitted, as-built and field-verified states.
- Never infer tank size from bedrooms, parcel area, occupancy or building type and present it as a fact.
- Unknown values remain null, never zero or fabricated defaults.
- Candidate sales services must be reviewed against evidence, capability, site access and current service history.
- No property-level records, addresses, owner names, personal contact information, or raw permit scans in this public repository.

## Validation tests to implement before private ingestion
1. Reject negative/zero physical capacities and invalid units.
2. Require provenance for every populated physical specification.
3. Ensure design_flow_gpd and tank_capacity_gallons are stored separately.
4. Ensure permitted design never becomes field_verified without independent inspection evidence.
5. Preserve conflicting historical designs with their document dates.
6. Verify public Pages build excludes property-level evidence.
