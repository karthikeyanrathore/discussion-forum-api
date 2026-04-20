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
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from anthropic import Anthropic

# ── Config ────────────────────────────────────────────────────────────────────

BERLIN_TZ       = ZoneInfo("Europe/Berlin")
EVENTS_PATH     = Path("modules/poc_scripts/btu-kal/data/calendar_events_full.json")
ANTHROPIC_MODEL = "claude-sonnet-4-6"
MAX_TOKENS      = 1024

SYSTEM_PROMPT = """You are a helpful calendar assistant for BTU Cottbus-Senftenberg AI Master's students.

You answer questions about the student's class schedule using the calendar data provided.

Rules:
- Always answer based ONLY on the calendar data provided in the context.
- Be specific about room locations, times, and course names.
- If asked about "today" or "tomorrow", use the current date provided.
- If no classes are found for the exact requested day but data for a nearby day is provided, 
  clearly say "I don't have data for that exact day, but here is the nearest available schedule:"
- Format times in a readable way (e.g., "9:15 AM - 10:45 AM").
- Keep answers concise and clear.
- If a course name is in German, provide the English name if available.
- Always mention the room/location when available.
- When showing course room/location, show ALL occurrences found (past and future).
- If the same course appears multiple times, list ALL rooms and times for each occurrence."""

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


def search_by_course_name(events: list[dict], query: str) -> list[dict]:
    """
    Search events by course name or course code.
    Searches across the ENTIRE calendar (past + future).
    Case-insensitive partial match on course_name, course_name_de, summary, course_code.
    """
    query_lower = query.lower()

    # Extract meaningful keywords — remove common question words
    stopwords = {
        "where", "is", "the", "room", "for", "when", "what", "time",
        "does", "start", "class", "course", "lecture", "find", "my",
        "do", "i", "have", "a", "an", "in", "at", "on", "of", "how"
    }
    keywords = [
        word for word in query_lower.split()
        if word not in stopwords and len(word) > 2
    ]

    if not keywords:
        return []

    matched = []
    for event in events:
        searchable = " ".join([
            event.get("course_name", ""),
            event.get("course_name_de", ""),
            event.get("summary", ""),
            event.get("course_code", ""),
        ]).lower()

        # Match if ANY keyword found in the event's searchable text
        if any(kw in searchable for kw in keywords):
            matched.append(event)

    return matched


def is_course_search_query(query: str) -> bool:
    """
    Detect if query is asking about a specific course
    rather than a time-based query.
    """
    query_lower = query.lower()

    # Temporal keywords = NOT a course search
    temporal = [
        "today", "tomorrow", "this week", "next week",
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday", "weekend",
        "this month", "upcoming", "next class", "schedule"
    ]
    if any(t in query_lower for t in temporal):
        return False

    # Course search indicators — expanded list
    course_indicators = [
        "room for", "where is", "location of", "when is", "when does",
        "room of", "where are", "find the room", "which room",
        "where can i find", "location for"
    ]
    if any(ind in query_lower for ind in course_indicators):
        return True

    # If query contains "room" or "location" at all — likely a course search
    if "room" in query_lower or "location" in query_lower:
        return True

    return False


def filter_events_for_context(events: list[dict], query: str) -> list[dict]:
    """
    Intelligently filter events relevant to the query.
    Handles both temporal queries and course name searches.
    """
    now      = now_berlin()
    today    = now.date()
    tomorrow = today + timedelta(days=1)

    query_lower = query.lower()

    # ── Course name search (entire calendar) ──────────────────────────────────
    if is_course_search_query(query):
        results = search_by_course_name(events, query)
        if results:
            return results
        # If no course match found, fall through to temporal filtering

    # ── Temporal filters ──────────────────────────────────────────────────────
    if "today" in query_lower:
        results = [e for e in events if e["date"] == today.isoformat()]
        if not results:
            # Fallback: show nearest available day's events with a note
            future = [e for e in events if e["date"] > today.isoformat()]
            if future:
                nearest_date = future[0]["date"]
                return [e for e in future if e["date"] == nearest_date]
        return results

    elif "tomorrow" in query_lower:
        results = [e for e in events if e["date"] == tomorrow.isoformat()]
        if not results:
            # Fallback: show nearest future day
            future = [e for e in events if e["date"] > tomorrow.isoformat()]
            if future:
                nearest_date = future[0]["date"]
                return [e for e in future if e["date"] == nearest_date]
        return results

    elif "next week" in query_lower:
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
        week_end   = week_start + timedelta(days=6)
        return [
            e for e in events
            if week_start.isoformat() <= e["date"] <= week_end.isoformat()
        ]

    elif "this week" in query_lower or "week" in query_lower:
        week_start = today - timedelta(days=today.weekday())
        week_end   = week_start + timedelta(days=6)
        return [
            e for e in events
            if week_start.isoformat() <= e["date"] <= week_end.isoformat()
        ]

    elif "monday" in query_lower:
        return [e for e in events if e["weekday"] == "Monday"
                and e["date"] >= today.isoformat()][:10]

    elif "tuesday" in query_lower:
        return [e for e in events if e["weekday"] == "Tuesday"
                and e["date"] >= today.isoformat()][:10]

    elif "wednesday" in query_lower:
        return [e for e in events if e["weekday"] == "Wednesday"
                and e["date"] >= today.isoformat()][:10]

    elif "thursday" in query_lower:
        return [e for e in events if e["weekday"] == "Thursday"
                and e["date"] >= today.isoformat()][:10]

    elif "friday" in query_lower:
        return [e for e in events if e["weekday"] == "Friday"
                and e["date"] >= today.isoformat()][:10]

    elif "next class" in query_lower or "upcoming" in query_lower:
        future = [e for e in events if e["start"] >= now.isoformat()]
        return future[:5]

    else:
        # Generic: try course search first, then fall back to upcoming 30 days
        course_results = search_by_course_name(events, query)
        if course_results:
            return course_results

        cutoff   = (today + timedelta(days=30)).isoformat()
        upcoming = [
            e for e in events
            if e["date"] >= today.isoformat() and e["date"] <= cutoff
        ]
        return upcoming[:20]


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
        "Where is the room for Cryptography?",
        "What classes do I have this week?",
        "What time does my first class start on Monday?",
        "Do I have any classes on Friday?",
        "What is my next upcoming class?",
        "When is Neural Networks and Learning Theory?",
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