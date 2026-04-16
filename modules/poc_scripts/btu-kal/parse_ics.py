"""
01_parse_ics.py
Parses a BTU calendar ICS file into structured JSON.

Usage:
    python modules/poc_scripts/btu-kal/parse_ics.py --ics path/to/calendar.ics

Output:
    modules/poc_scripts/btu-kal/data/calendar_events.json  (gitignored)

NOTE: The ICS file and output JSON are private and must NOT be committed.
      Add *.ics and data/ to .gitignore.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from icalendar import Calendar

# ── Config ────────────────────────────────────────────────────────────────────

BERLIN_TZ   = ZoneInfo("Europe/Berlin")
OUTPUT_PATH = Path("modules/poc_scripts/btu-kal/data/calendar_events.json")

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_berlin(dt) -> datetime | None:
    """Convert any datetime to Europe/Berlin timezone."""
    if dt is None:
        return None
    if hasattr(dt, "hour"):
        # It's a datetime
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=BERLIN_TZ)
        return dt.astimezone(BERLIN_TZ)
    else:
        # It's a date (all-day event) — convert to midnight Berlin time
        return datetime(dt.year, dt.month, dt.day, 0, 0, 0, tzinfo=BERLIN_TZ)


def parse_summary(summary: str) -> dict:
    """
    Parse course summary like:
    '120210 - Data Warehouses / Data-Warehouse-Technologien'
    into course_code and course_name.
    """
    if " - " in summary:
        parts       = summary.split(" - ", 1)
        course_code = parts[0].strip()
        course_name = parts[1].strip()
    else:
        course_code = ""
        course_name = summary.strip()

    # Also extract english name if format is "English / Deutsch"
    if " / " in course_name:
        names       = course_name.split(" / ", 1)
        course_name = names[0].strip()   # prefer English name
        course_name_de = names[1].strip()
    else:
        course_name_de = course_name

    return {
        "course_code":    course_code,
        "course_name":    course_name,
        "course_name_de": course_name_de,
    }


# ── Main parser ───────────────────────────────────────────────────────────────

def parse_ics(ics_path: str) -> list[dict]:
    """Parse ICS file and return list of structured event dicts."""
    with open(ics_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    events = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary  = str(component.get("SUMMARY", "")).strip()
        location = str(component.get("LOCATION", "")).strip()
        desc     = str(component.get("DESCRIPTION", "")).strip()
        uid      = str(component.get("UID", "")).strip()

        dt_start = to_berlin(component.get("DTSTART").dt if component.get("DTSTART") else None)
        dt_end   = to_berlin(component.get("DTEND").dt   if component.get("DTEND")   else None)

        if not dt_start or not summary:
            continue

        parsed = parse_summary(summary)

        event = {
            "uid":            uid,
            "summary":        summary,
            "course_code":    parsed["course_code"],
            "course_name":    parsed["course_name"],
            "course_name_de": parsed["course_name_de"],
            "location":       location or "N/A",
            "description":    desc or "N/A",
            "start":          dt_start.isoformat(),
            "end":            dt_end.isoformat() if dt_end else None,
            "date":           dt_start.strftime("%Y-%m-%d"),
            "weekday":        dt_start.strftime("%A"),          # Monday, Tuesday...
            "start_time":     dt_start.strftime("%H:%M"),       # 09:15
            "end_time":       dt_end.strftime("%H:%M") if dt_end else None,
        }

        events.append(event)
        print(
            f"  ✓ {event['date']} {event['weekday']} "
            f"{event['start_time']}-{event['end_time']} | "
            f"{event['course_name'][:40]} | {event['location'][:30]}"
        )

    # Sort by start datetime
    events.sort(key=lambda e: e["start"])
    return events


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Parse BTU ICS calendar file")
    parser.add_argument(
        "--ics",
        required=True,
        help="Path to your BTU calendar .ics file"
    )
    args = parser.parse_args()

    ics_path = Path(args.ics)
    if not ics_path.exists():
        print(f"ERROR: ICS file not found: {ics_path}")
        return

    print(f"Parsing: {ics_path}\n")
    events = parse_ics(str(ics_path))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! {len(events)} events saved to {OUTPUT_PATH}")
    print(f"   (This file is gitignored — keep your ICS data private)")


if __name__ == "__main__":
    main()