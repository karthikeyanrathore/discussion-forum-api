"""
02_query_calendar.py
Date-aware calendar query engine for BTU course schedule.

Supports natural queries like:
  - "Where is the room for Machine Learning today?"
  - "What classes do I have tomorrow?"
  - "When is the next Data Warehouses lecture?"
  - "What do I have this week?"
  - "What time does Deep Learning start on Monday?"

Usage (standalone test):
    python modules/poc_scripts/btu-kal/02_query_calendar.py

Usage (as module):
    from modules.poc_scripts.btu-kal.query_calendar import query_calendar
    result = query_calendar("What classes do I have tomorrow?")
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from anthropic import Anthropic

# ── Config ────────────────────────────────────────────────────────────────────

BERLIN_TZ      = ZoneInfo("Europe/Berlin")
EVENTS_PATH    = Path("modules/poc_scripts/btu-kal/data/calendar_events.json")
ANTHROPIC_MODEL = "claude-sonnet-4-6"
MAX_TOKENS      = 1024

SYSTEM_PROMPT = """You are a helpful calendar assistant for BTU Cottbus-Senftenberg AI Master's students.

You answer questions about the student's class schedule using the calendar data provided.

Rules:
- Always answer based ONLY on the calendar data provided in the context.
- Be specific about room locations, times, and course names.
- If asked about "today" or "tomorrow", use the current date provided.
- If no classes are found for a given day, clearly say so.
- Format times in a readable way (e.g., "9:15 AM - 10:45 AM").
- Keep answers concise and clear.
- If a course name is in German, provide the English name if available.
- Always mention the room/location when available."""

# ── Helpers ───────────────────────────────────────────────────────────────────

def now_berlin() -> datetime:
    """Current datetime in Berlin timezone."""
    return datetime.now(BERLIN_TZ)


def load_events() -> list[dict]:
    """Load parsed calendar events from JSON."""
    if not EVENTS_PATH.exists():
        raise FileNotFoundError(
            f"Events file not found: {EVENTS_PATH}\n"
            "Run 01_parse_ics.py first."
        )
    with open(EVENTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def filter_events_for_context(events: list[dict], query: str) -> list[dict]:
    """
    Intelligently filter events relevant to the query to keep context small.
    Detects temporal keywords and filters accordingly.
    """
    now      = now_berlin()
    today    = now.date()
    tomorrow = today + timedelta(days=1)

    query_lower = query.lower()

    # Detect temporal intent
    if "today" in query_lower:
        target_date = today.isoformat()
        return [e for e in events if e["date"] == target_date]

    elif "tomorrow" in query_lower:
        target_date = tomorrow.isoformat()
        return [e for e in events if e["date"] == target_date]

    elif "this week" in query_lower or "week" in query_lower:
        # Monday to Sunday of current week
        week_start = today - timedelta(days=today.weekday())
        week_end   = week_start + timedelta(days=6)
        return [
            e for e in events
            if week_start.isoformat() <= e["date"] <= week_end.isoformat()
        ]

    elif "next week" in query_lower:
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
        week_end   = week_start + timedelta(days=6)
        return [
            e for e in events
            if week_start.isoformat() <= e["date"] <= week_end.isoformat()
        ]

    elif "monday" in query_lower:
        day_events = [e for e in events if e["weekday"] == "Monday" and e["date"] >= today.isoformat()]
        return day_events[:10]

    elif "tuesday" in query_lower:
        day_events = [e for e in events if e["weekday"] == "Tuesday" and e["date"] >= today.isoformat()]
        return day_events[:10]

    elif "wednesday" in query_lower:
        day_events = [e for e in events if e["weekday"] == "Wednesday" and e["date"] >= today.isoformat()]
        return day_events[:10]

    elif "thursday" in query_lower:
        day_events = [e for e in events if e["weekday"] == "Thursday" and e["date"] >= today.isoformat()]
        return day_events[:10]

    elif "friday" in query_lower:
        day_events = [e for e in events if e["weekday"] == "Friday" and e["date"] >= today.isoformat()]
        return day_events[:10]

    else:
        # Generic query — return upcoming events (next 30 days)
        cutoff = (today + timedelta(days=30)).isoformat()
        upcoming = [
            e for e in events
            if e["date"] >= today.isoformat() and e["date"] <= cutoff
        ]
        return upcoming[:20]  # cap to avoid huge context


def format_events_as_context(events: list[dict]) -> str:
    """Format events list into readable text for Claude."""
    if not events:
        return "No events found for the requested period."

    lines = []
    for e in events:
        lines.append(
            f"- {e['weekday']} {e['date']} | "
            f"{e['start_time']} - {e['end_time']} | "
            f"{e['course_name']} ({e['course_code']}) | "
            f"Room: {e['location']}"
        )
    return "\n".join(lines)


# ── Core query function ───────────────────────────────────────────────────────

def query_calendar(question: str) -> dict:
    """
    Answer a calendar question using relevant events + Claude.

    Returns:
        {
            "answer": str,
            "events_used": int,
            "current_datetime": str
        }
    """
    events = load_events()
    now    = now_berlin()

    relevant_events = filter_events_for_context(events, question)
    context         = format_events_as_context(relevant_events)

    user_message = (
        f"Current date and time (Berlin/Germany): {now.strftime('%A, %d %B %Y, %H:%M')}\n\n"
        f"Student's class schedule:\n"
        f"{context}\n\n"
        f"Student's question: {question}"
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set.")

    client   = Anthropic(api_key=api_key)
    response = client.messages.create(
        model      = ANTHROPIC_MODEL,
        max_tokens = MAX_TOKENS,
        system     = SYSTEM_PROMPT,
        messages   = [{"role": "user", "content": user_message}],
    )

    return {
        "answer":           response.content[0].text,
        "events_used":      len(relevant_events),
        "current_datetime": now.strftime("%A, %d %B %Y, %H:%M %Z"),
    }


# ── Standalone test ───────────────────────────────────────────────────────────

def main():
    test_queries = [
        "What classes do I have today?",
        "What do I have tomorrow?",
        "Where is the room for Data Warehouses?",
        "What classes do I have this week?",
        "What time does my first class start on Monday?",
        "Do I have any classes on Friday?",
        "What is my next upcoming class?",
    ]

    print(f"Current Berlin time: {now_berlin().strftime('%A, %d %B %Y, %H:%M')}\n")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQ: {query}")
        print("-" * 40)
        try:
            result = query_calendar(query)
            print(f"A: {result['answer']}")
            print(f"   (used {result['events_used']} events from calendar)")
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            break
        except Exception as e:
            print(f"ERROR: {e}")
        print()


if __name__ == "__main__":
    main()