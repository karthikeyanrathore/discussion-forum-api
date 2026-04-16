# BTU Calendar POC (`btu-kal`)

A date-aware calendar query engine for the BTU AI Master's schedule.
Parses ICS files and answers natural language questions about classes,
rooms, and times using Claude.

---

## Setup

```bash
pip install icalendar python-dateutil anthropic
```

Export `ANTHROPIC_API_KEY` in your environment.

---

## How to run

### Step 1 — Parse your ICS file
Download your calendar from the BTU portal as an ICS file.
Then run:

```bash
python modules/poc_scripts/btu-kal/01_parse_ics.py --ics /path/to/your/calendar.ics
```

This creates `modules/poc_scripts/btu-kal/data/calendar_events.json`
which is **gitignored** — your schedule stays private.

### Step 2 — Query the calendar

```bash
python modules/poc_scripts/btu-kal/02_query_calendar.py
```

---

## Sample queries

| Query | What it does |
|-------|-------------|
| `"What classes do I have today?"` | Lists all events for today |
| `"What do I have tomorrow?"` | Lists tomorrow's events |
| `"Where is the room for Data Warehouses?"` | Finds room for a specific course |
| `"What classes do I have this week?"` | Full week overview |
| `"What time does my first class start on Monday?"` | Day-specific query |
| `"Do I have any classes on Friday?"` | Checks a specific weekday |
| `"What is my next upcoming class?"` | Next class from now |
| `"Is there any class this Thursday?"` | Day availability check |

---

## File structure

```
btu-kal/
  01_parse_ics.py        ← ICS parser → calendar_events.json
  02_query_calendar.py   ← date-aware query engine using Claude
  requirements.txt       ← dependencies
  README.md              ← this file
  .gitignore             ← ignores *.ics and data/
  data/                  ← GITIGNORED — your private calendar data
    calendar_events.json ← parsed events (generated, not committed)
```

---

## ICS event fields used

| ICS Field | Used as |
|-----------|---------|
| `SUMMARY` | Course code + name |
| `DTSTART` | Start datetime (converted to Berlin TZ) |
| `DTEND` | End datetime |
| `LOCATION` | Room / building |
| `DESCRIPTION` | Additional info |

---

## Privacy

- **Never commit** `.ics` files
- **Never commit** `data/calendar_events.json`
- Both are in `.gitignore`