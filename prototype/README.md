# Dr. Poo Sales Intelligence: Concept Prototype

This is a zero-dependency, static browser application. No PostgreSQL, build tooling, paid services, or CRM access is required.

## Run

Open `index.html` in any modern browser. Alternatively, from this directory run `python3 -m http.server 8000` and visit `http://localhost:8000`.

## Features

- 60 **synthetic** prospect records distributed across Duval, Clay, St. Johns, Nassau, and Baker counties
- Residential maintenance, repairs/replacements, new installations, grease trap, commercial wastewater, and emergency service segments
- Interactive KPI cards, county and strategy summaries, prospect filtering and sorting by priority score
- Status changes persisted in the browser's localStorage, reset control, and CSV export

## Security and data limitations

All data is fabricated for interface evaluation. No actual septic system, property owner, or customer data is present. Scores and opportunity values are illustrative. localStorage is **not** suitable for production customer data, shared team workflows, or secure authentication. The GitHub repository is private, but the prototype has no login and should not be deployed publicly with real customer data.

## Next phase

1. Confirm sales manager workflow and CRM/field-service vendor.
2. Connect to verified public septic GIS and permit records, preserving source and confidence.
3. Introduce authenticated hosting, shared persistence, permissions, audit history, and customer suppression before any real customer records are loaded.
4. Evaluate whether Postgres/PostGIS is justified by actual data volume and geographic querying needs.
