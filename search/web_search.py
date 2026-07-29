import requests
from typing import List, Dict

class WebSearchEngine:
    """Performs web search queries and URL summarization."""

    def __init__(self, max_results: int = 5):
        self.max_results = max_results

    def search(self, query: str) -> List[Dict[str, str]]:
        """Executes web search query returning title, link, and snippet."""
        import datetime
        current_year = str(datetime.datetime.now().year)

        # Enhance query with current year if query requests latest/recent results without a year
        enhanced_query = query
        if any(w in query.lower() for w in ["latest", "recent", "current", "race", "standings", "score", "f1", "news"]) and not any(y in query for y in ["2024", "2025", "2026"]):
            enhanced_query = f"{query} {current_year}"

        results = []
        # Attempt duckduckgo search package (ddgs or duckduckgo_search)
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                ddg_gen = ddgs.text(enhanced_query, max_results=self.max_results)
                for r in ddg_gen:
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
                if results:
                    return results
        except Exception as e:
            print(f"[SearchEngine] DuckDuckGo API notice: {e}")

        # Fallback to HTML API / Wikipedia lookup
        try:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
            r = requests.get(wiki_url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                results.append({
                    "title": data.get("title", query),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "snippet": data.get("extract", "")
                })
        except Exception:
            pass

        if not results:
            results.append({
                "title": f"Search Results for '{query}'",
                "url": f"https://duckduckgo.com/?q={requests.utils.quote(query)}",
                "snippet": f"Web search for '{query}' executed. Open link to view full query results."
            })

        return results

    def format_search_results_for_llm(self, query: str, results: List[Dict[str, str]]) -> str:
        """Formats search results as context for the language model."""
        context = f"### Web Search Results for Query: '{query}'\n\n"
        for i, res in enumerate(results, 1):
            context += f"**[{i}] {res['title']}**\nURL: {res['url']}\nSnippet: {res['snippet']}\n\n"
        return context
