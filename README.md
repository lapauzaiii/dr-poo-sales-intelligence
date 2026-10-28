# Dr. Poo Sales Intelligence: evidence-first ATU/PBTS alpha

Five-county Northeast Florida market intelligence for **Baker, Clay, Duval, Nassau and St. Johns**. The production UI is static and served through Cloudflare Pages; the project uses no database or paid API. Pages runs `python3 scripts/build_static.py` and serves only the allowlisted `dist/` output, not repository scripts, tests or historical fixtures.

## What is actually live

- [ATU/PBTS intelligence](prototype/atu-pbts.html): official maintenance-entity permits by county (March report) and a separate newer product-sorted provider listing (September report), with report dates, PDF page provenance, county/product filters, CSV export and source health.
- [DEP septic inventory](prototype/inventory.html): grouped historical septic-likelihood records from Florida DEP ArcGIS, using independently verified Florida DOR `CO_NO` county codes.
- [Official source coverage](data/equipment-source-validation.json): documented access limitations and data acquisition targets.
- [Verified installed systems](data/atu-pbts-systems.json) and [evidence-backed opportunities](data/opportunities.json): **empty** until authorized, installation-level records are validated. An empty verified feed is correct, not a defect.

The two maintenance reports are **not** installation inventories. Maintenance permits identify providers permitted for specific products; they do not establish system counts, contract expirations or open sales opportunities. A source may be old even if the collector checked it today.

## Automated workflows

- [Official ATU/PBTS maintenance intelligence](.github/workflows/atu-pbts-maintenance.yml): daily fetch of the official Florida DEP county and product reports, PDF parsing, unit tests, privacy and schema validation, fail-closed publication and GitHub Actions logs.
- [Florida DEP septic inventory aggregates](.github/workflows/septic-inventory.yml): daily grouped ArcGIS fetch, source checks and validated snapshot commit.
- Source failures fail the job and **do not overwrite the last validated file**. Inspect workflow logs and source-health dates before interpreting results.

## Local development and validation

```bash
python3 -m http.server 8000
# Open http://localhost:8000/prototype/
python3 -m unittest discover -s tests -v
python3 scripts/validate_alpha.py
python3 scripts/check_frontend.py   # requires node
```

Maintenance collector requires `pdftotext` from poppler-utils and downloads only the documented Florida DEP public report. Run `python3 scripts/fetch_maintenance_entities.py` to refresh. It never persists the downloaded PDF or business contact details.

## Data provenance and county-code distinction

Inventory `CO_NO` is a **DOR code**: Baker 12, Clay 20, Duval 26, Nassau 55, St. Johns 65. The maintenance report uses **separate permit jurisdiction prefixes**: Clay 10-QC, Duval 16-QJ, St. Johns 55-QS. Never join the two datasets on the numeric code alone.

## Security and scope

The repository is **public**. No customer information, parcel numbers, owner names, property addresses, personal phone numbers, CRM data or private credentials may be committed. Cloudflare Access protects the main production hostname, but review access policies and preview-domain coverage separately. No access policies are changed by the collectors. The system costs no additional paid service and should remain under the $50/month cap.

See [alpha release and recovery notes](docs/ALPHA_RELEASE.md). Do not interpret a successful Pages deployment as proof of access-policy coverage or live data freshness.
