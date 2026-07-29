"""
utils/fuzzy_match.py — Lightweight Typo Tolerance & Fuzzy String Matcher
Uses Python standard library difflib for instant, zero-dependency fuzzy matching.
"""
import difflib
from typing import List, Optional


def is_fuzzy_match(text: str, target_keyword: str, threshold: float = 0.70) -> bool:
    """
    Returns True if target_keyword (or a close typo variant) is present in text.
    Handles typos like 'wether' -> 'weather', 'opn' -> 'open', 'shwtdwn' -> 'shutdown'.
    """
    if not text or not target_keyword:
        return False

    text_lower = text.lower()
    target_lower = target_keyword.lower()

    # Exact substring match first
    if target_lower in text_lower:
        return True

    # Token-level fuzzy match
    tokens = [t.strip(" .,!?:;\"'()[]{}") for t in text_lower.split() if len(t.strip(" .,!?:;\"'()[]{}")) >= 2]
    target_len = len(target_lower)

    for token in tokens:
        # Ignore tokens with huge length differences
        if abs(len(token) - target_len) > 3:
            continue
        ratio = difflib.SequenceMatcher(None, token, target_lower).ratio()
        if ratio >= threshold:
            return True

    return False


def matches_any_fuzzy(text: str, keywords: List[str], threshold: float = 0.70) -> bool:
    """Returns True if any keyword in keywords fuzzy matches the input text."""
    return any(is_fuzzy_match(text, kw, threshold=threshold) for kw in keywords)


def find_best_fuzzy_match(word: str, candidates: List[str], threshold: float = 0.65) -> Optional[str]:
    """
    Finds the best matching candidate for a given word or typo.
    Example: 'notpad' -> 'notepad', 'discrd' -> 'discord', 'brve' -> 'brave'.
    """
    if not word or not candidates:
        return None

    word_lower = word.lower().strip(" .,!?:;\"'()[]{}")
    matches = difflib.get_close_matches(word_lower, [c.lower() for c in candidates], n=1, cutoff=threshold)
    if matches:
        best_lower = matches[0]
        # Return original case candidate
        for c in candidates:
            if c.lower() == best_lower:
                return c
    return None
