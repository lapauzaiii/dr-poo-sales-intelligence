#!/usr/bin/env python3
"""Static production HTML checks. Uses preinstalled Node.js for JavaScript syntax."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", *(ROOT / "prototype").glob("*.html")]

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
    def handle_data(self, data):
        if self.in_script and data.strip():
            self.parts.append(data)

def main():
    assert not (ROOT / "data" / "permit-intelligence.json").exists(), "Synthetic permit fixture must not ship"
    for path in PAGES:
        html = path.read_text(encoding="utf-8")
        assert "Sample prospect" not in html and "DEMO DATA ONLY" not in html, path
        p = Scripts()
        p.feed(html)
        for js in p.parts:
            result = subprocess.run(["node", "--check", "-"], input=js, capture_output=True, text=True)
            if result.returncode:
                raise ValueError(f"{path}: JavaScript syntax error: {result.stderr}")
    dashboard = (ROOT / "prototype" / "atu-pbts.html").read_text(encoding="utf-8")
    assert "maintenance-entities.json" in dashboard
    assert "atu-pbts-systems.json" in dashboard
    assert "opportunities.json" in dashboard
    assert "csvCell" in dashboard
    print("PASS: production HTML syntax, evidence sources, safe export, no synthetic permit fixture")

if __name__ == "__main__":
    main()
