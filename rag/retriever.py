"""
rag/retriever.py — Phase 5: RAG Retriever
Performs fast TF-IDF keyword search over indexed local file chunks
and formats results for injection into LLM prompts.
"""
import re
import math
from collections import Counter
from typing import List, Dict
from pathlib import Path


class RAGRetriever:
    """
    Retrieves the most relevant indexed file chunks for a given query.
    Uses pure-Python TF-IDF scoring — no external ML dependencies.
    Falls back to simple keyword overlap if needed.
    """

    def __init__(self, db):
        """
        Args:
            db: DatabaseMemory instance
        """
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Searches all indexed chunks and returns the top_k most relevant.
        Each result: {filepath, text, score, index}
        """
        all_chunks = self.db.get_all_rag_chunks()
        if not all_chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored = []
        for chunk in all_chunks:
            chunk_tokens = self._tokenize(chunk["text"])
            score = self._tfidf_score(query_tokens, chunk_tokens, len(all_chunks))
            if score > 0:
                scored.append({
                    "filepath": chunk["filepath"],
                    "filename": Path(chunk["filepath"]).name,
                    "text": chunk["text"],
                    "index": chunk["index"],
                    "score": score
                })

        if not scored:
            # Fallback for general queries ("summarize my pdf", "uploaded file"): return initial chunks of indexed files
            return [{
                "filepath": chunk["filepath"],
                "filename": Path(chunk["filepath"]).name,
                "text": chunk["text"],
                "index": chunk["index"],
                "score": 1.0
            } for chunk in all_chunks[:top_k]]

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


    def format_context(self, results: List[Dict]) -> str:
        """
        Formats retrieved chunks into a clean string for LLM prompt injection.
        """
        if not results:
            return ""

        lines = ["📚 Relevant content from your local knowledge base:"]
        for i, r in enumerate(results, 1):
            lines.append(f"\n--- Source {i}: {r['filename']} ---")
            # Truncate very long chunks
            text = r["text"]
            if len(text) > 600:
                text = text[:600] + "..."
            lines.append(text)

        return "\n".join(lines)

    def answer_from_knowledge_base(self, query: str, ai_provider) -> str:
        """
        Retrieves relevant chunks and asks AI to answer based on them.
        """
        results = self.search(query, top_k=5)
        if not results:
            return "I couldn't find anything relevant in your local knowledge base. Try indexing a folder first using the Knowledge Base panel."

        context = self.format_context(results)
        source_files = list({r["filename"] for r in results})

        try:
            response = ai_provider.generate_response(
                messages=[{"sender": "User", "content": query}],
                system_prompt=(
                    f"You are Jarvis, a helpful AI assistant. Answer the user's question based on the following content "
                    f"retrieved from their local files:\n\n{context}\n\n"
                    f"If the answer isn't in the provided content, say so clearly. "
                    f"Always cite which file the information came from."
                )
            )
            return f"{response}\n\n📄 *Sources: {', '.join(source_files)}*"
        except Exception as e:
            return f"RAG retrieval error: {e}"

    # ------------------------------------------------------------------
    # Internal: TF-IDF scoring
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        """Lowercases, removes punctuation, splits into tokens, removes stop words."""
        STOP_WORDS = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "this", "that", "these", "those", "it", "its", "i", "you",
            "he", "she", "we", "they", "my", "your", "our", "their",
            "and", "or", "but", "if", "then", "so", "as", "not"
        }
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', text.lower())
        return [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]

    def _tfidf_score(self, query_tokens: List[str], doc_tokens: List[str], corpus_size: int) -> float:
        """
        Computes a simplified TF-IDF score between query and document tokens.
        """
        if not doc_tokens:
            return 0.0

        doc_counter = Counter(doc_tokens)
        doc_len = len(doc_tokens)
        score = 0.0

        for token in query_tokens:
            tf = doc_counter.get(token, 0) / doc_len
            # Simplified IDF: assume moderate rarity for all terms
            idf = math.log(1 + corpus_size / (1 + doc_counter.get(token, 0)))
            score += tf * idf

        return score
