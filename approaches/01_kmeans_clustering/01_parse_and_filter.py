import re
import json
from pathlib import Path

# ── config ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "chat.txt"
OUT_FILE = PROJECT_ROOT / "data" / "processed" / "questions.json"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── parse whatsapp lines ─────────────────────────────────
def parse_whatsapp(filepath):
    pattern = re.compile(
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s\d{1,2}:\d{2}:\d{2}\s[AP]M\]\s(.+?):\s(.+)$"
    )
    messages = []
    current = None

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = pattern.match(line)
            if match:
                if current:
                    messages.append(current)
                date, author, text = match.groups()
                current = {"date": date, "text": text}
            elif current:
                current["text"] += " " + line
        if current:
            messages.append(current)

    return messages

# ── language detection (basic) ───────────────────────────
def is_english(text: str) -> bool:
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if non_ascii / max(len(text), 1) > 0.15:
        return False

    non_english_words = [
        "ki", "ke", "ka", "hai", "hain", "koi", "kya", "kisi", "mujhe",
        "mein", "nahi", "bhi", "aur", "yeh", "toh", "pass", "wala",
        "ich", "ist", "nicht", "aber", "und", "oder", "auch", "bitte",
        "danke", "wie", "was", "wann", "warum", "welche", "können",
        "gibt", "haben", "sein", "werden"
    ]
    words = text.lower().split()
    non_en_count = sum(1 for w in words if w in non_english_words)
    if non_en_count >= 2:
        return False

    return True

# ── social/logistical noise filter (NEW) ────────────────
NOISE_PATTERNS = [
    # "Anyone taking/enrolled in X?"
    r"^anyone (taking|doing|enrolled|joining|attending|in|have|got)",
    # "Anyone have notes/material/pdf?"
    r"anyone (have|has|got|share|send|sending).{0,40}(notes|material|pdf|slides|book|link|file|drive)",
    # "Is there class/lecture today?"
    r"(is there|any) (class|lecture|lab|session|seminar).{0,20}(today|tomorrow|tonight|now|cancelled|cancel)",
    # "Hi does anyone..." social openers
    r"^(hi|hello|hey).{0,20}(anyone|anybody|someone|somebody)",
    # "Anyone free/online?"
    r"anyone (free|online|available|around|there|here)",
    # "German A1/B2 anyone?"
    r"(german|english|language).{0,20}anyone",
    # Asking for group links
    r"(whatsapp|telegram|discord|group).{0,20}(link|invite|add me)",
    # Asking to share contact
    r"(share|send|give).{0,20}(number|contact|whatsapp|phone)",
    # "Who is attending X?"
    r"^who (is|are|will).{0,30}(attending|coming|joining|going)",
    # "Anyone want to study together?"
    r"(study|meet).{0,20}(together|anyone|group|join)",
    # "Does anyone have X course/module?" — resource sharing not process questions
    r"(does anyone|do you).{0,20}have.{0,30}(course|module|subject|neuroadaptive|seminar)",
    # Apartment/accommodation seeking — social not procedural
    r"(looking for|need|want|any|available).{0,30}(apartment|flat|room|roommate|flatmate|place to stay|housing)",
    r"(apartment|flat|room).{0,20}(available|anyone|free|sharing|share|needed|looking)",
    # Assignment sharing requests
    r"(assignment|homework|task).{0,20}(anyone|share|send|have|done|solution|help me)",
    r"(can|could) (you|anyone|someone).{0,20}(share|send|help).{0,20}(assignment|homework)",
]

NOISE_COMPILED = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]

def is_social_noise(text: str) -> bool:
    return any(p.search(text) for p in NOISE_COMPILED)

# ── link remover ─────────────────────────────────────────
def remove_links(text: str) -> str:
    """Remove URLs and WhatsApp-style links from text."""
    # Remove http/https URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove www. links
    text = re.sub(r'www\.\S+', '', text)
    # Remove leftover whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ── relevance check ──────────────────────────────────────
def is_relevant(text: str) -> bool:
    text_lower = text.lower()

    if len(text.strip()) < 20:
        return False

    reject_patterns = [
        r"\bcan i dm\b", r"\bdm me\b", r"\bprivate(ly)?\b",
        r"\banyone (already|who will|coming|there|available)\b",
        r"\bwho('s| is) (coming|joining|attending|there)\b",
        r"\bsee you\b", r"\btake care\b", r"\bgood luck\b",
        r"\bget well\b", r"\bhappy\b", r"\bcongrat\b",
        r"\bsorry\b", r"\bthank(s| you)\b",
        r"\bwhat('s| is) your\b",
        r"\bwhere are you\b",
        r"\bhow are you\b",
        r"\bcan (we|you) meet\b",
        r"\bwant to (hang|meet|talk)\b",
        r"\bwho else\b",
        r"\banyone (want|wanna|going)\b",
        r"\bfood\b", r"\brestaurant\b", r"\bcafe\b",
        r"\bparty\b", r"\bdrink\b",
    ]
    for pattern in reject_patterns:
        if re.search(pattern, text_lower):
            return False

    relevant_keywords = [
        "course", "module", "lecture", "seminar", "exam", "examination",
        "moodle", "registration", "register", "enroll", "credit", "ects",
        "grade", "grading", "pass", "fail", "retake", "resit",
        "thesis", "dissertation", "supervisor", "topic",
        "internship", "praktikum", "report", "submission", "deadline",
        "assignment", "project", "presentation",
        "btu", "university", "faculty", "department", "professor",
        "portal", "zpa", "primuss", "lsf", "library",
        "semester", "winter", "summer", "timetable", "schedule",
        "class", "tutorial", "exercise", "lab",
        "certificate", "transcript", "degree", "master", "bachelor",
        "visa", "residence", "permit", "anmeldung", "registration office",
        "blocked account", "health insurance", "krankenkasse",
        "accommodation", "apartment", "wohnheim", "dormitory", "room",
        "stipend", "scholarship", "bafög", "financing",
        "language course", "german course", "sprachkurs",
        "ai", "artificial intelligence", "machine learning", "data",
        "python", "programming", "algorithm", "neural", "deep learning",
    ]
    if not any(kw in text_lower for kw in relevant_keywords):
        return False

    return True

# ── question detection ───────────────────────────────────
def is_question(text: str) -> bool:
    text = text.strip()

    skip_phrases = [
        "omitted", "joined using", "left", "added", "removed",
        "changed the group", "changed their phone", "tap to message",
        "\u200e", "null"
    ]
    if any(p in text.lower() for p in skip_phrases):
        return False

    if len(text) < 20:
        return False

    if text.endswith("?"):
        return True

    question_starters = (
        "how", "what", "when", "where", "who", "why", "which",
        "is ", "are ", "can ", "could ", "do ", "does ", "did ",
        "should ", "would ", "has ", "have ", "will ", "any ", "anyone ",
        "is there", "does anyone", "do we", "do i"
    )
    if text.lower().startswith(question_starters):
        return True

    return False

# ── main ─────────────────────────────────────────────────
def main():
    print(f"Reading: {RAW_FILE}")
    messages = parse_whatsapp(RAW_FILE)
    print(f"Total messages parsed: {len(messages)}")
    
       # ── Clean links from all messages ──
    for m in messages:
        m["text"] = remove_links(m["text"])

    questions = [m for m in messages if is_question(m["text"])]
    print(f"After question filter:     {len(questions)}")

    english_questions = [q for q in questions if is_english(q["text"])]
    print(f"After language filter:     {len(english_questions)}")

    no_noise = [q for q in english_questions if not is_social_noise(q["text"])]
    print(f"After noise filter:        {len(no_noise)}")

    relevant_questions = [q for q in no_noise if is_relevant(q["text"])]
    print(f"After relevance filter:    {len(relevant_questions)}")

    # Save clean questions
    output = [{"date": q["date"], "question": q["text"]} for q in relevant_questions]
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved {len(output)} clean questions to: {OUT_FILE}")

    # Save rejected by noise filter so you can review
    noise_rejected = [q for q in english_questions if is_social_noise(q["text"])]
    rejected_file = OUT_FILE.parent / "rejected_noise.json"
    with open(rejected_file, "w", encoding="utf-8") as f:
        json.dump([{"date": q["date"], "question": q["text"]} for q in noise_rejected],
                  f, ensure_ascii=False, indent=2)
    print(f"🗑️  Rejected noise saved to: {rejected_file} ({len(noise_rejected)} messages)")
    print("   → Review this file to tune filters if needed\n")

    print("--- Sample clean questions ---")
    for q in output[:10]:
        print(f"  {q['question']}")

if __name__ == "__main__":
    main()