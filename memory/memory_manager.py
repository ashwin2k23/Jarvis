"""
MemoryManager — Phase 1: Long-Term Conversational Memory
Automatically extracts facts from user messages and injects relevant context
into every LLM system prompt so Jarvis always remembers key information.
"""
import re
import datetime
from typing import Optional


# Regex-based fact extraction patterns: (pattern, category, key_template)
EXTRACTION_PATTERNS = [
    # Identity
    (r"my name is\s+([A-Za-z\s]+)", "personal", "user_name"),
    (r"i(?:'m| am) called\s+([A-Za-z\s]+)", "personal", "user_name"),
    (r"call me\s+([A-Za-z\s]+)", "personal", "user_name"),
    (r"i(?:'m| am)\s+(\d+)\s+years? old", "personal", "user_age"),
    (r"i(?:'m| am) from\s+([A-Za-z\s,]+)", "personal", "user_location"),
    (r"i live in\s+([A-Za-z\s,]+)", "personal", "user_location"),
    (r"i(?:'m| am) a(?:n)?\s+([A-Za-z\s]+student|engineer|developer|designer|doctor|teacher|student)", "personal", "user_profession"),

    # Work & Projects
    (r"my internship\s+(?:starts?|begins?|is)\s+([\w\s,]+)", "work", "internship_date"),
    (r"i(?:'m| am) interning at\s+([A-Za-z\s]+)", "work", "internship_company"),
    (r"i work at\s+([A-Za-z\s]+)", "work", "employer"),
    (r"i(?:'m| am) working on\s+([A-Za-z\s0-9]+)", "projects", "current_project"),
    (r"my project is\s+([A-Za-z\s0-9]+)", "projects", "current_project"),
    (r"my deadline is\s+([\w\s,]+)", "work", "deadline"),
    (r"my(?:\s+company|\s+job|\s+role) is\s+([A-Za-z\s]+)", "work", "job_role"),

    # Preferences
    (r"i prefer\s+([A-Za-z\s]+)", "preferences", "general_preference"),
    (r"i like\s+([A-Za-z\s]+)", "preferences", "likes"),
    (r"i don'?t like\s+([A-Za-z\s]+)", "preferences", "dislikes"),
    (r"my favorite\s+(\w+)\s+is\s+([A-Za-z\s0-9]+)", "preferences", "favorite"),
    (r"i use\s+([A-Za-z0-9\s]+)\s+(?:for|as my)", "preferences", "tools_used"),

    # Reminders & dates
    (r"remind me (?:to|about)\s+(.+?)(?:\s+on\s+([\w\s,]+))?$", "reminders", "reminder"),
    (r"remember that\s+(.+)", "reminders", "note"),
    (r"(?:my|the)\s+(\w+)\s+is\s+(?:on|at|next)\s+([\w\s,]+)", "reminders", "event_date"),
    (r"(?:my|the)\s+(\w+)\s+(?:starts?|begins?)\s+([\w\s,]+)", "reminders", "event_start"),

    # Tech / Coding preferences
    (r"i(?:'m| am) using\s+([A-Za-z0-9\s\.\-]+)\s+(?:framework|library|language|stack)", "preferences", "tech_stack"),
    (r"my (?:main|primary) language is\s+([A-Za-z\s#\+]+)", "preferences", "programming_language"),
]


class MemoryManager:
    """
    Manages long-term conversational memory for Jarvis.

    - Automatically extracts facts from user messages via regex patterns.
    - Injects relevant memory context into LLM system prompts.
    - Supports natural language recall queries.
    """

    def __init__(self, db):
        """
        Args:
            db: DatabaseMemory instance from memory.db
        """
        self.db = db

    # ------------------------------------------------------------------
    # Fact Extraction
    # ------------------------------------------------------------------

    def extract_and_save(self, text: str) -> list:
        """
        Scans user text for memory-worthy facts and persists them to the DB.
        Returns list of (category, key, value) tuples that were saved.
        """
        text_lower = text.lower().strip()
        saved = []

        for pattern, category, key_template in EXTRACTION_PATTERNS:
            try:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # Multi-group match (e.g. "my X is Y on Z")
                        parts = [m.strip() for m in match if m.strip()]
                        value = " ".join(parts)
                        key = f"{key_template}_{parts[0][:20].replace(' ', '_')}" if len(parts) > 1 else key_template
                    else:
                        value = match.strip()
                        key = key_template

                    if value and len(value) > 1:
                        # Clean up value
                        value = re.sub(r'\s+', ' ', value).strip(" .,!?;")
                        if len(value) > 200:
                            value = value[:200]

                        self.db.save_memory_fact(category, key, value)
                        saved.append((category, key, value))
            except Exception:
                continue

        return saved

    # ------------------------------------------------------------------
    # Context Retrieval for LLM
    # ------------------------------------------------------------------

    def get_relevant_context(self, query: str) -> str:
        """
        Retrieves memory facts relevant to the given query.
        Returns a formatted string ready to inject into the LLM system prompt.
        """
        if not query or len(query.strip()) < 3:
            return ""

        # Search by keywords from the query
        query_words = [w for w in re.split(r'\W+', query.lower()) if len(w) > 2]
        found_facts = []
        seen_keys = set()

        for word in query_words:
            results = self.db.search_memory_facts(word)
            for fact in results:
                if fact["key"] not in seen_keys:
                    seen_keys.add(fact["key"])
                    found_facts.append(fact)

        if not found_facts:
            return ""

        lines = ["📝 Relevant memory about this user:"]
        for fact in found_facts[:8]:
            lines.append(f"  • [{fact['category'].upper()}] {fact['key'].replace('_', ' ')}: {fact['value']}")

        return "\n".join(lines)

    def get_full_context_for_prompt(self) -> str:
        """
        Returns ALL stored memory facts formatted for the LLM system prompt.
        Used when no specific query is available (e.g. general conversation).
        """
        all_facts = self.db.get_all_memory_facts()
        if not all_facts:
            return ""

        # Group by category
        categories: dict = {}
        for fact in all_facts:
            cat = fact["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"{fact['key'].replace('_', ' ')}: {fact['value']}")

        lines = ["📋 What Jarvis knows about this user:"]
        for cat, facts in categories.items():
            lines.append(f"  [{cat.upper()}]")
            for f in facts[:10]:  # Cap per-category to avoid prompt bloat
                lines.append(f"    • {f}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Manual Memory Save (for explicit "remember that..." commands)
    # ------------------------------------------------------------------

    def save_explicit_fact(self, category: str, key: str, value: str):
        """Directly saves a fact — used for explicit user commands."""
        self.db.save_memory_fact(category, key, value)

    def forget_fact(self, key: str):
        """Deletes a specific fact by key name."""
        self.db.delete_memory_fact(key)

    def recall_fact(self, query: str) -> Optional[str]:
        """
        Tries to directly answer a memory recall question with typo tolerance.
        Returns a formatted answer string or None if nothing found.
        """
        results = self.db.search_memory_facts(query)

        # Fallback to fuzzy matching if exact SQL LIKE yields no result
        if not results:
            from utils.fuzzy_match import is_fuzzy_match
            all_facts = self.db.get_all_memory_facts()
            query_words = [w for w in re.split(r'\W+', query.lower()) if len(w) >= 3]
            matched_facts = []
            seen_keys = set()
            for fact in all_facts:
                key_clean = fact["key"].replace("_", " ")
                for word in query_words:
                    if is_fuzzy_match(key_clean, word, threshold=0.68) or is_fuzzy_match(fact["value"], word, threshold=0.68):
                        if fact["key"] not in seen_keys:
                            seen_keys.add(fact["key"])
                            matched_facts.append(fact)
            results = matched_facts

        if not results:
            return None

        # Build a natural language answer
        if len(results) == 1:
            f = results[0]
            return f"I remember: **{f['key'].replace('_', ' ').title()}**: {f['value']}"
        else:
            lines = ["Here's what I remember:"]
            for f in results[:5]:
                lines.append(f"• **{f['key'].replace('_', ' ').title()}**: {f['value']}")
            return "\n".join(lines)

    # ------------------------------------------------------------------
    # Detect explicit memory commands
    # ------------------------------------------------------------------

    @staticmethod
    def is_memory_command(text: str) -> bool:
        """Returns True if the user text is a memory-related command."""
        from utils.fuzzy_match import matches_any_fuzzy
        return matches_any_fuzzy(text, [
            "remember that", "remind me", "don't forget", "make a note",
            "save this", "keep in mind", "forget that", "what do you know about",
            "do you remember", "what did i tell you about"
        ])

    @staticmethod
    def is_recall_query(text: str) -> bool:
        """Returns True if user is asking Jarvis to recall something from memory."""
        from utils.fuzzy_match import matches_any_fuzzy
        recall_patterns = [
            "when does", "when is", "when did", "what is my", "what's my",
            "do you remember", "what did i", "when do i", "where is my",
            "who is my", "what was", "remind me about"
        ]
        return matches_any_fuzzy(text, recall_patterns)
