import json
import os
from dataclasses import dataclass
from datetime import time as Time

MODEL = "gemini-2.5-flash"
MAX_SUGGESTIONS = 3
MIN_SUGGESTIONS = 2
PRIORITIES = ("low", "med", "high")
DAY_START = 6 * 60       # earliest suggested start, in minutes after midnight
DAY_END = 22 * 60        # latest a suggested task may finish
SLOT_STEP = 30

# Words that only make sense for one species; used by the species-sanity guardrail.
FORBIDDEN_WORDS = {
    "cat": ("walk", "leash"), #should check that owners are still able to "walk or leash train cat" if writing up their own bc it's possible for cat owners to do this 
    "dog": ("litter",),
    "other": ("litter", "leash"),
}

SYSTEM_PROMPT = """You help pet owners plan their daily pet care.
Given a pet's name and species (cat, dog, or other), suggest 3 common DAILY care tasks
specific to that species, personalized with the pet's name (e.g. "Feed Jiji").
Cats need litter box scooping and never walks. Dogs need walks and never litter boxes.
Every pet needs feeding and some play or attention.
Return JSON only: a list of objects with keys
  title (string), duration (integer minutes, 1-240),
  priority ("low" | "med" | "high"), preferred_time ("HH:MM", 24-hour, between 06:00 and 21:00).
Spread the preferred times across the day."""

EXAMPLES = """Example for a cat named Jiji:
[{"title": "Feed Jiji", "duration": 10, "priority": "high", "preferred_time": "08:00"},
 {"title": "Scoop Litter Box", "duration": 10, "priority": "med", "preferred_time": "12:00"},
 {"title": "Play with Jiji", "duration": 15, "priority": "med", "preferred_time": "18:00"}]
Example for a dog named Max:
[{"title": "Feed Max", "duration": 10, "priority": "high", "preferred_time": "08:00"},
 {"title": "Walk Max", "duration": 30, "priority": "high", "preferred_time": "17:00"},
 {"title": "Play with Max", "duration": 15, "priority": "med", "preferred_time": "19:00"}]"""

# Fallback templates: (title, duration, priority, "HH:MM")
FALLBACK = {
    "cat": [
        ("Feed {name}", 10, "high", "08:00"),
        ("Scoop Litter Box", 10, "med", "12:00"),
        ("Play with {name}", 15, "med", "18:00"),
    ],
    "dog": [
        ("Feed {name}", 10, "high", "08:00"),
        ("Walk {name}", 30, "high", "17:00"),
        ("Play with {name}", 15, "med", "19:00"),
    ],
    "other": [
        ("Feed {name}", 10, "high", "08:00"),
        ("Check {name}'s water and habitat", 10, "med", "12:00"),
        ("Spend time with {name}", 15, "low", "18:00"),
    ],
}


@dataclass
class Suggestion:
    title: str
    duration: int
    priority: str
    start_time: Time


def _to_minutes(t):
    return t.hour * 60 + t.minute


def _overlaps(start, duration, busy):
    return any(start < b_start + b_dur and b_start < start + duration for b_start, b_dur in busy)


def assign_times(items, busy):
    """Place each (title, duration, priority, preferred Time) at the nearest free slot.

    `busy` is a list of (start_minutes, duration) for existing tasks. Slots never overlap
    busy intervals or each other, and stay within the day window. Returns Suggestions;
    items that cannot be placed are dropped.
    """
    busy = list(busy)
    placed = []
    for title, duration, priority, preferred in items:
        target = _to_minutes(preferred)
        # Try the preferred time first, then step outward (later, then earlier).
        offsets = [0]
        for k in range(1, (DAY_END - DAY_START) // SLOT_STEP + 1):
            offsets += [k * SLOT_STEP, -k * SLOT_STEP]
        for off in offsets:
            start = target + off
            if start < DAY_START or start + duration > DAY_END:
                continue
            if not _overlaps(start, duration, busy):
                busy.append((start, duration))
                placed.append(Suggestion(title, duration, priority, Time(start // 60, start % 60)))
                break
    placed.sort(key=lambda s: s.start_time)
    return placed


def _parse_time(value):
    hh, mm = str(value).split(":")
    return Time(int(hh), int(mm))


def validate(raw_items, species):
    """Schema + species-sanity checks. Returns clean (title, duration, priority, Time) tuples."""
    forbidden = FORBIDDEN_WORDS.get(species, FORBIDDEN_WORDS["other"])
    clean, seen = [], set()
    for item in raw_items if isinstance(raw_items, list) else []:
        try:
            title = str(item["title"]).strip()
            duration = int(item["duration"])
            priority = str(item["priority"]).strip().lower()
            preferred = _parse_time(item["preferred_time"])
        except (KeyError, TypeError, ValueError):
            continue
        if not title or not 1 <= duration <= 240 or priority not in PRIORITIES:
            continue
        if any(word in title.lower() for word in forbidden):
            continue
        if title.lower() in seen:
            continue
        seen.add(title.lower())
        clean.append((title, duration, priority, preferred))
    return clean[:MAX_SUGGESTIONS]


def call_gemini(name, species):
    """Ask Gemini for suggestions; returns the parsed JSON. Raises on any failure."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=f"{EXAMPLES}\n\nNow the pet: name={name!r}, species={species!r}.",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            http_options=types.HttpOptions(timeout=15000),
        ),
    )
    return json.loads(response.text)


def fallback_items(name, species):
    templates = FALLBACK.get(species, FALLBACK["other"])
    return [(t.format(name=name), d, p, _parse_time(tm)) for t, d, p, tm in templates]


def suggest_tasks(name, species, busy=(), llm=call_gemini):
    """Return (suggestions, source) where source is "ai" or "fallback".

    Falls back to the rules table when the LLM errors or yields fewer than
    MIN_SUGGESTIONS valid items. `busy` is a list of (start_minutes, duration).
    """
    items, source = [], "fallback"
    try:
        items = validate(llm(name, species), species)
        if len(items) >= MIN_SUGGESTIONS:
            source = "ai"
    except Exception:
        items = []
    if source == "fallback":
        items = fallback_items(name, species)
    return assign_times(items, busy), source
