# Dr. Poo production alpha frontend

The previous synthetic-prospect prototype was retired. The production entry point now redirects to `atu-pbts.html`, the evidence-only ATU/PBTS dashboard.

- `atu-pbts.html` reads official maintenance-entity permits, verified installation feed (currently empty), evidence-backed opportunities (currently empty), and source health.
- `inventory.html` shows historical Florida DEP septic inventory aggregates for Baker, Clay, Duval, Nassau and St. Johns.
- `intelligence.html` is a compatibility redirect. It no longer displays fabricated permits or competitor data.
- `index.html` redirects to the ATU/PBTS page.

Serve the repository root with `python3 -m http.server 8000` and visit `http://localhost:8000/prototype/`. Do not open these files using `file://`, because browser fetch requests need an HTTP server.

This repository is public. Never publish property records, owners, personal contacts, or CRM data. Cloudflare Access protects the production hostname but team permissions and preview-hostname coverage require independent verification. See `../docs/ALPHA_RELEASE.md`.
