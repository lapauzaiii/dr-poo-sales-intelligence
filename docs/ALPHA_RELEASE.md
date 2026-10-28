# Alpha release, validation and recovery

Status: 2026-10-28. Scope: Baker, Clay, Duval, Nassau, St. Johns, Florida. Priority: ATU/PBTS; lift stations deferred.

## Acceptance matrix

| Requirement | Status | Evidence / limitation |
| --- | --- | --- |
| Cloudflare Access | Configured; scope requires review | Owner-review Access app exists on the Pages hostname; access policy currently allows one owner email. Other team access and preview subdomains not verified. |
| Territory | Implemented | DOR inventory CO_NO 12/20/26/55/65; separate maintenance permit prefixes 10-QC/16-QJ/55-QS. |
| Septic inventory | Automated | Daily ArcGIS grouped counts; historical inventory only, not ATU counts or new permits. |
| ATU/PBTS equipment records | No verified installations | Source contract exists and returns an explicit empty dataset. Operating-permit export still needed. |
| Maintenance market | Automated | Official DEP county PDF dated March 31, 2026 (31 permits: Clay 3, Duval 23, St. Johns 5), plus September 15, 2026 product-sorted PDF (70 county/product/business listing rows: Baker 1, Clay 5, Duval 54, Nassau 2, St. Johns 8). Both have page-level provenance. |
| Opportunities | Evidence-only empty | No verified installation or contract availability means no opportunity claims. |
| Data quality | Implemented | Strict data type, date, county, ID uniqueness, source SHA256, product, privacy and empty-evidence checks. |
| Operations | Automated with logs | GitHub Actions daily schedules, fail-closed refresh, tests, and commit history. |
| Demo data | Removed from current production tree | Fabricated permit JSON and demo workflow deleted; old permit page redirects. Historic commits may still contain fixtures. |
| Cost | No new paid services | GitHub Actions, static Cloudflare Pages and public DEP endpoints. |

## Authoritative source inventory

1. Florida DEP FLWMI septic points: https://ags.dep.state.fl.us/arcgis/rest/services/OpenData/SEPTIC_SYSTEMS/MapServer/0 . Source describes known/likely/somewhat-likely wastewater method. The county code domain is corroborated by the official Florida DOH FLWMI Wastewater ArcGIS layer at https://maps.floridahealth.gov/server/rest/services/FLWMI/FLWMI_Wastewater/MapServer/0 .
2. Maintenance permits by county: https://floridadep.gov/sites/default/files/2026_0331_MEByCounty_1.pdf . Report run date 2026-03-31. This is the machine-parsed source for provider/product permissions.
3. More recent product-sorted maintenance list: https://floridadep.gov/sites/default/files/2026_0924_MEByProduct.pdf . Report run date 2026-09-15. Its table lacks the permit identifiers available in the county report. The separate product-sorted listing is now automatically ingested; it is not automatically joined to permit IDs or installations.
4. Florida DEP onsite program: https://floridadep.gov/water/onsite-sewage . County health departments remain the relevant local contact for most onsite system permitting. Public operating-permit exports with installation-level system type have not been validated.
5. MARS: https://mars.floridadep.gov/ . No authorized export credentials have been provided. Never scrape authenticated maintenance activity.

## Important distinctions

- Maintenance permit = authorized service capability. It is not a customer, installed ATU, contract, expiration date or lead.
- Inventory KnownSeptic = wastewater method certainty. It is not a conventional vs ATU classification.
- Baker/Nassau absent from the March 2026 maintenance report is **not** proof of zero providers, zero systems or no market.
- Multiple permits can belong to one business. The dashboard shows permit counts and distinct printed names, not a resolved legal-entity count.
- A collector checked on October 28 does not make the March 31 agency report current. The dashboard displays both dates.

## Operations and troubleshooting

**Maintenance refresh:** Both the county permit report and newer product-sorted report are fetched and validated. In GitHub Actions open `Official ATU PBTS maintenance intelligence`, inspect the last scheduled or manual run and its steps. Unit tests run first. The parser downloads only the allowlisted official PDF, validates magic bytes/size, runs `pdftotext -layout`, and requires valid date, permit IDs, nonempty product lists and minimum expected coverage. If source layout changes, the workflow fails and leaves the previous snapshot intact. Fix the parser and add a regression test; do not weaken the checks or fabricate rows. The workflow compares candidate snapshots against current main and retries publication without force-pushing. If another run already published the same source with a newer retrieval time, it preserves that newer snapshot.

**Inventory refresh:** In GitHub Actions open `Florida DEP septic inventory aggregates`. The ArcGIS collector refuses empty, truncated, negative or malformed grouped results. Regression tests and schema validation run before publication. The candidate is saved separately, then compared with the latest validated `main` snapshot after each fetch/reset; older or equal retrievals are never republished. Source URL and official county-mapping authority must remain unchanged, retrieval timestamps must be timezone-aware and not future-dated, and publication uses an atomic file replacement. Concurrent pushes retry up to five times without force. Failed fetches or invalid candidates preserve the last valid file. See `tests/test_inventory_publication.py` and `scripts/publish_inventory_snapshot.py`.

**Deployment:** Cloudflare Pages is GitHub-connected to `main` and builds an isolated 11-file allowlisted artifact with `python3 scripts/build_static.py`. Check the Pages deployment's commit hash and successful status against GitHub before claiming release. A successful build does not prove end-user login or every preview hostname is protected.

**Data quality:** Run `python -m unittest discover -s tests -v`, `python scripts/validate_alpha.py`, and `python scripts/check_frontend.py`. Never overwrite validated data with synthetic fixtures. Do not publish personal information from source PDFs.

**Recovery:** Revert the problematic commit or restore the last validated JSON snapshot through GitHub. Check that the production deployment tracks the desired commit, then rerun tests and the relevant workflow. Document failures in the Actions logs and release notes.

## Remaining blockers before team-ready beta

1. **Team access:** Owner-only Access policy currently protects the Pages hostname. The Dr. Poo team requires separately approved Access policy changes. Do not expand access without explicit owner authorization.
2. **Installed-unit intelligence:** Request an authorized five-county ATU/PBTS operating-permit export, ideally county, permit identifier, system category, make/model, permit status, issued/renewal dates, and source reference. Minimize personal/property information and confirm commercial reuse rights.
3. **Maintenance freshness:** The county report is March 31, 2026, while the product report is September 15, 2026. Both are ingested separately. Reconcile business aliases and changing provider permissions only after establishing reliable entity identity. Treat report age explicitly.
4. **Cloudflare preview security:** Validate whether deployment preview hostnames and any custom domains are covered by the intended Access policy before publishing sensitive data. Current app contains only non-sensitive public aggregate/business data.
5. **Shared review workflow:** No durable shared opportunity dispositions exist. Keep opportunities empty until a secure authenticated backend and approved evidence are available.

## Definition of an acceptable alpha

A fully operational **evidence-first alpha** may have zero verified ATU installations and zero opportunities. It must show why, still deliver accurate inventory and maintenance-permission data, expose freshness and source links, and fail safely when sources are unavailable. It must never quietly substitute synthetic records.
