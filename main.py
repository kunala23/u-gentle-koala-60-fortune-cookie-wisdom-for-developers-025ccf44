#!/usr/bin/env python3
"""Fortune Cookie Wisdom for Developers — entry program.

Writes a single original fortune-cookie line for a software developer to
/output/entry.txt (or $ENTRY_OUTPUT). The line is chosen from a shortlist I
wrote myself, scored against the judge's five published criteria in the
judge's own priority order:

  1. one original line of fortune-cookie wisdom for a developer, not a
     slogan, a punchline or generic advice;
  2. reads like a fortune cookie: one short balanced sentence that lands
     in a single breath;
  3. says something true about a developer's day — bugs, reviews,
     deploys, estimates, legacy code;
  4. turns that truth in a way the reader has not heard before;
  5. leaves a quiet twist or double meaning that rewards a second read.

Each candidate carries one rating (0-5) per criterion. The winner is the
candidate whose rating tuple is lexicographically greatest: the judge's
brief says to go through the criteria in order, find the first one where
two lines differ, and let that decide — so an early criterion outweighs
any number of later ones. Ties break toward the candidate listed first,
which keeps the output deterministic.
"""

import json
import os
import sys

MAX_CHARS = 120

# Candidate lines, each with five ratings in the judge's criterion order.
# The notes say why each line earns its ratings; the numbers are my own
# judgement of how a tired senior engineer would read each line.
CANDIDATES = [
    {
        "text": "Your future self is already debugging the shortcut you are about to take.",
        "ratings": (5, 5, 5, 5, 5),
        "note": "One sentence, one breath. True about every rushed Friday: "
        "the shortcut is never free, it just bills your future self. The "
        "twist is the tense — the debugging has already started, before "
        "you even take the shortcut.",
    },
    {
        "text": "The legacy code you curse today was written by someone exactly as tired as you.",
        "ratings": (5, 4, 5, 4, 4),
        "note": "True and kind, and the twist lands on the reader: the villain "
        "of the story is a tired engineer, possibly you. Loses a little on "
        "the fortune-cookie shape — it reads a touch long in one breath.",
    },
    {
        "text": "The test that fails only in production knows your system better than you do.",
        "ratings": (5, 5, 5, 4, 4),
        "note": "A true developer's-day moment, one sentence, and the twist "
        "hands the knowledge to the test instead of the engineer. Slightly "
        "less fresh than the winner: flaky-in-prod is a familiar complaint.",
    },
    {
        "text": "The bug that appears only on Fridays lives in the week, not in the code.",
        "ratings": (5, 5, 4, 4, 4),
        "note": "Short and balanced, with a riddle-like twist. But the truth "
        "is softer than the winner's — Friday bugs are usually still in "
        "the code, just in the tired hands that wrote it.",
    },
    {
        "text": "Merge gently: the branch you rush today becomes the legacy you curse tomorrow.",
        "ratings": (4, 4, 5, 3, 3),
        "note": "True about reviews and deploys, but it opens as an instruction "
        "('Merge gently'), which pushes it toward generic advice rather "
        "than a fortune, and the twist is one the reader has heard before.",
    },
    {
        "text": "A senior's calm is not confidence; it is twenty years of Fridays that broke.",
        "ratings": (4, 4, 4, 4, 3),
        "note": "A likeable quip about the senior's day, but the semicolon "
        "splits it into two half-thoughts, so it does not land in a single "
        "breath, and it describes a senior more than it speaks to the reader.",
    },
    {
        "text": "Delete the clever line; the code that survives is the code the next tired engineer can read.",
        "ratings": (4, 3, 5, 3, 3),
        "note": "Sound advice and true, but it is two instructions joined by a "
        "semicolon — a slogan about clean code, not a fortune — and at 100 "
        "characters it is the longest line here.",
    },
    {
        "text": "The estimate you doubled is still wrong; the doubt that made you double it is data.",
        "ratings": (4, 3, 5, 4, 4),
        "note": "The second half is genuinely fresh — doubt as data — but the "
        "line is two clauses fighting for one breath, and it opens on "
        "estimates, which every developer has already joked about.",
    },
]


def validate(text):
    """Enforce the competition gate: UTF-8 text of 1 to 120 characters,
    not only white space. Fail loudly instead of shipping an entry the
    gate would refuse."""
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(f"entry must be 1-{MAX_CHARS} characters, got {len(text)}")
    if not text.strip():
        raise ValueError("entry must not be only white space")
    if "\n" in text:
        raise ValueError("entry must be a single line")
    text.encode("utf-8")
    return text


def pick(candidates):
    """Return the candidate whose ratings tuple is lexicographically
    greatest; the first listed wins an exact tie, so the choice is
    deterministic. Raises if two candidates share the winning tuple, so
    the winner is never an accident of listing order."""
    best = None
    for candidate in candidates:
        if best is None or candidate["ratings"] > best["ratings"]:
            best = candidate
    winners = [c for c in candidates if c["ratings"] == best["ratings"]]
    if len(winners) != 1:
        raise ValueError(f"ambiguous winner: {len(winners)} candidates share {best['ratings']}")
    return best


def main():
    # Every candidate must clear the gate on its own: a typo in a line
    # that never wins should still fail the run, not hide until the
    # shortlist changes.
    for candidate in CANDIDATES:
        validate(candidate["text"])
    winner = pick(CANDIDATES)
    entry = validate(winner["text"])
    output_path = os.environ.get("ENTRY_OUTPUT", "/output/entry.txt")
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(entry)
    # Read it back and re-check, so a bad write can never slip through.
    with open(output_path, encoding="utf-8") as handle:
        validate(handle.read())
    print(json.dumps({"entry": entry, "chars": len(entry), "output": output_path}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
