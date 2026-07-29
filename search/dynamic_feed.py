import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

class DynamicFeedEngine:
    """Fetches and structures multi-source real-time news, trending topics, tech news, videos, and newsletter digests."""

    FEED_SOURCES = {
        "world": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "tech": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
        "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
        "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US&ceid=US:en",
        "science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US&ceid=US:en",
    }

    def _fetch_rss_articles(self, url: str, limit: int = 8) -> List[Dict[str, Any]]:
        articles = []
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall("./channel/item")[:limit]:
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    pub_date = item.findtext("pubDate", "")
                    source = item.findtext("source", "Google News")

                    if pub_date and len(pub_date) > 16:
                        pub_date = pub_date[:16]

                    articles.append({
                        "title": title,
                        "link": link,
                        "source": source,
                        "pub_date": pub_date,
                        "snippet": f"Live coverage from {source}."
                    })
        except Exception as e:
            print(f"[DynamicFeed Engine] RSS fetch notice: {e}")
        return articles

    def fetch_news_feed(self, category: str = "world", query: str = None) -> List[Dict[str, Any]]:
        """Fetches REAL-TIME news articles from Google News RSS."""
        if query:
            url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        else:
            url = self.FEED_SOURCES.get(category.lower(), self.FEED_SOURCES["world"])

        articles = self._fetch_rss_articles(url, limit=8)

        if not articles:
            # Fallback if network offline
            articles = [{
                "title": "Network Unavailable — Connect to Internet for Live News",
                "link": "https://news.google.com",
                "source": "Jarvis Feed",
                "pub_date": "Now",
                "snippet": "Check network connection to refresh real-time feeds."
            }]
        return articles

    def fetch_trending_topics(self) -> List[Dict[str, Any]]:
        """Fetches REAL-TIME trending topics from live Google News top stories."""
        live_items = self._fetch_rss_articles(self.FEED_SOURCES["world"], limit=5)
        trends = []

        for i, item in enumerate(live_items, 1):
            title = item.get("title", "Trending Headline")
            # Extract main topic name before dash
            topic_name = title.split(" - ")[0] if " - " in title else title
            source = item.get("source", "Web Trend")

            trends.append({
                "rank": i,
                "topic": topic_name[:65],
                "tag": "Live Trend",
                "reason": f"Top trending headline reported by {source}.",
                "source": source,
                "summary": f"Full Article: {title}",
                "link": item.get("link")
            })

        return trends

    def fetch_tech_ai_feed(self) -> List[Dict[str, Any]]:
        """Fetches REAL-TIME AI & Technology updates from Google News Technology RSS."""
        live_items = self._fetch_rss_articles(self.FEED_SOURCES["tech"], limit=6)
        tech_cards = []

        for item in live_items:
            title = item.get("title", "")
            source = item.get("source", "Tech Media")

            # Determine company / category tag
            company = "Tech Industry"
            for c in ["OpenAI", "Google", "Microsoft", "Apple", "NVIDIA", "Meta", "Amazon", "Tesla", "Anthropic"]:
                if c.lower() in title.lower():
                    company = c
                    break

            tech_cards.append({
                "company": company,
                "badge": "Real-time Tech",
                "title": title,
                "summary": f"Reported live by {source} ({item.get('pub_date', 'Today')}).",
                "link": item.get("link")
            })

        return tech_cards

    def fetch_video_feed(self, query: str = "popular videos") -> List[Dict[str, Any]]:
        """Fetches REAL-TIME YouTube video items matching exact search query."""
        if not query or not query.strip():
            query = "popular videos"

        search_url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
        videos = []
        seen = set()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            resp = requests.get(search_url, headers=headers, timeout=6)
            if resp.status_code == 200:
                import re
                # Match videoId and title in YouTube initialData
                raw_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
                raw_titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', resp.text)

                for vid, title in zip(raw_ids, raw_titles):
                    if vid not in seen and len(videos) < 6:
                        seen.add(vid)
                        videos.append({
                            "video_id": vid,
                            "title": f"▶ {title}",
                            "channel": "YouTube Stream",
                            "duration": "Watch Now",
                            "views": f"Result for '{query}'",
                            "embed_url": f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1",
                            "link": f"https://www.youtube.com/watch?v={vid}"
                        })
        except Exception as e:
            print(f"[DynamicFeed] YouTube video fetch notice: {e}")

        # Fallback: DuckDuckGo Video search if YouTube regex missed items
        if len(videos) < 3:
            try:
                try:
                    from ddgs import DDGS
                except ImportError:
                    from duckduckgo_search import DDGS

                with DDGS() as ddgs:
                    ddg_vids = ddgs.videos(query, max_results=6)
                    for r in ddg_vids:
                        v_url = r.get("content", "") or r.get("embed_url", "")
                        import re
                        v_match = re.search(r'(?:v=|\/embed\/|\/watch\?v=)([a-zA-Z0-9_-]{11})', v_url)
                        v_id = v_match.group(1) if v_match else ""
                        if v_id and v_id not in seen and len(videos) < 6:
                            seen.add(v_id)
                            videos.append({
                                "video_id": v_id,
                                "title": f"▶ {r.get('title', query)}",
                                "channel": r.get("publisher", "YouTube"),
                                "duration": r.get("duration", "Watch"),
                                "views": f"Result for '{query}'",
                                "embed_url": f"https://www.youtube-nocookie.com/embed/{v_id}?autoplay=1",
                                "link": f"https://www.youtube.com/watch?v={v_id}"
                            })
            except Exception as e:
                print(f"[DynamicFeed] DDG video search notice: {e}")

        return videos



    def generate_newsletter_digest(self) -> Dict[str, Any]:
        """Generates an executive Morning Brief newsletter digest from real-time live feeds."""
        world_items = self._fetch_rss_articles(self.FEED_SOURCES["world"], limit=2)
        tech_items = self._fetch_rss_articles(self.FEED_SOURCES["tech"], limit=2)
        biz_items = self._fetch_rss_articles(self.FEED_SOURCES["business"], limit=2)

        sections = []
        if world_items:
            sections.append({
                "heading": "🌍 World & Global Events",
                "text": f"• {world_items[0]['title']}\n• {world_items[1]['title'] if len(world_items) > 1 else ''}"
            })
        if tech_items:
            sections.append({
                "heading": "💻 Technology & AI",
                "text": f"• {tech_items[0]['title']}\n• {tech_items[1]['title'] if len(tech_items) > 1 else ''}"
            })
        if biz_items:
            sections.append({
                "heading": "📈 Business & Markets",
                "text": f"• {biz_items[0]['title']}\n• {biz_items[1]['title'] if len(biz_items) > 1 else ''}"
            })

        return {
            "title": "📰 Jarvis Executive Live Newsletter",
            "date": "Real-Time Intelligence Brief",
            "sections": sections
        }
