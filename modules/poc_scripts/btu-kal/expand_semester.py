"""
03_expand_semester.py
Expands a single week of parsed calendar events into a full semester
by repeating each event weekly until the semester end date.

BTU AI MSc Summer Semester 2026:
  Start: 2026-04-13 (Monday, first week already in calendar_events.json)
  End:   2026-07-18 (Saturday, end of lecture period)

Usage:
    python modules/poc_scripts/btu-kal/03_expand_semester.py

Input:  modules/poc_scripts/btu-kal/data/calendar_events.json
Output: modules/poc_scripts/btu-kal/data/calendar_events_full.json
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# ── Config ────────────────────────────────────────────────────────────────────

BERLIN_TZ    = ZoneInfo("Europe/Berlin")
INPUT_PATH   = Path("modules/poc_scripts/btu-kal/data/calendar_events.json")
OUTPUT_PATH  = Path("modules/poc_scripts/btu-kal/data/calendar_events_full.json")

# BTU Summer Semester 2026 lecture period
SEMESTER_END = "2026-07-18"

# ── Main ──────────────────────────────────────────────────────────────────────

def expand_to_semester(events: list[dict], semester_end: str) -> list[dict]:
    """
    Take one week of events and repeat each event weekly
    until semester_end date.
    """
    end_date    = datetime.strptime(semester_end, "%Y-%m-%d").date()
    all_events  = []
    seen_keys   = set()  # avoid duplicates

    for event in events:
        original_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        current_date  = original_date

        while current_date <= end_date:
            # Build new event for this week's occurrence
            new_event = event.copy()

            # Update date-related fields
            date_str  = current_date.isoformat()
            new_event["date"] = date_str

            # Update start/end ISO strings by replacing the date portion
            if event["start"]:
                time_part         = event["start"][10:]   # e.g. "T09:15:00+02:00"
                new_event["start"] = date_str + time_part

            if event["end"]:
                time_part        = event["end"][10:]
                new_event["end"] = date_str + time_part

            # Unique key to avoid duplicates
            key = f"{new_event['uid']}_{date_str}"
            if key not in seen_keys:
                seen_keys.add(key)
                all_events.append(new_event)

            # Jump to same weekday next week
            current_date += timedelta(weeks=1)

    # Sort by date then start time
    all_events.sort(key=lambda e: (e["date"], e["start_time"]))
    return all_events


def main():
    if not INPUT_PATH.exists():
        print(f"Input not found: {INPUT_PATH}")
        print("Run 01_parse_ics.py first.")
        return

    with open(INPUT_PATH, encoding="utf-8") as f:
        events = json.load(f)

    print(f"Loaded {len(events)} events from one week\n")
    print(f"Expanding to full semester (until {SEMESTER_END})...\n")

    full_events = expand_to_semester(events, SEMESTER_END)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(full_events, f, ensure_ascii=False, indent=2)

    # Summary
    dates = sorted(set(e["date"] for e in full_events))
    print(f"✅ Done! {len(full_events)} total events across {len(dates)} days")
    print(f"   First day : {dates[0]}")
    print(f"   Last day  : {dates[-1]}")
    print(f"   Saved to  : {OUTPUT_PATH}")
    print(f"\n   Now update EVENTS_PATH in query_calendar.py to use this file.")


if __name__ == "__main__":
    main()