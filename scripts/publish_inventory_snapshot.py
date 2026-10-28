#!/usr/bin/env python3
"""Publish only a newer validated DEP inventory snapshot.

The daily collector can race with maintenance refreshes or another inventory run.
Compare against the current main branch after fetching it, never replay an older
snapshot over a newer retrieval, and write the selected file atomically.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import tempfile

from validate_alpha import validate_inventory


def parsed_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Inventory retrieval timestamp must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def should_publish(current: dict, candidate: dict, now: dt.datetime | None = None) -> bool:
    """Return False for a stale/equal retrieval, raise on invalid evidence."""
    validate_inventory(current)
    validate_inventory(candidate)
    if candidate["source_url"] != current["source_url"]:
        raise ValueError("Inventory source URL changed unexpectedly")
    if candidate.get("county_mapping_source") != current.get("county_mapping_source"):
        raise ValueError("Inventory county mapping authority changed unexpectedly")
    existing = parsed_time(current["retrieved_at"])
    incoming = parsed_time(candidate["retrieved_at"])
    clock = now or dt.datetime.now(dt.timezone.utc)
    if incoming > clock + dt.timedelta(minutes=10):
        raise ValueError("Candidate retrieval timestamp is in the future")
    return incoming > existing


def publish(candidate_path: Path, output_path: Path) -> bool:
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    current = json.loads(output_path.read_text(encoding="utf-8"))
    if not should_publish(current, candidate):
        print("Preserving newer or equally recent validated inventory snapshot")
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output_path.parent,
        prefix=".inventory-", suffix=".json", delete=False
    ) as handle:
        temp_path = Path(handle.name)
        try:
            json.dump(candidate, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temp_path.unlink(missing_ok=True)
            raise
    os.replace(temp_path, output_path)
    print("Published validated inventory retrieval", candidate["retrieved_at"])
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/septic-inventory-aggregate.json"))
    args = parser.parse_args()
    publish(args.candidate, args.output)


if __name__ == "__main__":
    main()
