"""
config.py
---------
All the "what" lives here so the "how" (fetch_news.py, summarize.py) never
needs to change when you want to add a category, swap a feed, or tweak
how many stories you get per section.

Feed choice: every feed below is the outlet's OWN official RSS feed (BBC,
The Guardian, Al Jazeera, NPR, TechCrunch, The Verge, etc.) - not a
re-packaged aggregator. That matters for two reasons: (1) it's free, no
API key, and (2) "reputable source" is enforced structurally, not just by
asking the LLM nicely.

Multiple feeds per category exist so that if one outlet has a quiet day
(or its feed URL breaks), the category still has enough material.
"""

CATEGORIES = {
    "World & Politics": {
        "top_n": 10,
        "keywords": None,  # None = no keyword filter, take everything
        "feeds": [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.theguardian.com/world/rss",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://feeds.npr.org/1004/rss.xml",
        ],
    },
    "Wars & Conflicts": {
        "top_n": 10,
        # Same broad world feeds as above, but filtered down to
        # conflict-related stories so Ukraine-Russia, Israel-Gaza,
        # US-Iran tensions, etc. all get a dedicated section instead of
        # competing with general politics for space.
        "keywords": [
            "war", "conflict", "military", "strike", "missile", "troops",
            "invasion", "ceasefire", "attack", "airstrike", "offensive",
            "ukraine", "russia", "iran", "israel", "gaza", "hamas",
            "hezbollah", "taiwan", "north korea", "rebels", "insurgent",
            "nuclear", "sanctions", "drone strike",
        ],
        "feeds": [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.theguardian.com/world/rss",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://feeds.npr.org/1004/rss.xml",
        ],
    },
    "Business & Economy": {
        "top_n": 10,
        "keywords": None,
        "feeds": [
            "http://feeds.bbci.co.uk/news/business/rss.xml",
            "https://www.theguardian.com/business/rss",
            "https://feeds.npr.org/1006/rss.xml",
        ],
    },
    "Science": {
        "top_n": 10,
        "keywords": None,
        "feeds": [
            "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "https://www.theguardian.com/science/rss",
            "https://feeds.npr.org/1007/rss.xml",
        ],
    },
    "Health": {
        "top_n": 10,
        "keywords": None,
        "feeds": [
            "http://feeds.bbci.co.uk/news/health/rss.xml",
            "https://www.theguardian.com/society/rss",
            "https://feeds.npr.org/1128/rss.xml",
        ],
    },
    "Sports": {
        "top_n": 10,
        "keywords": None,
        "feeds": [
            "http://feeds.bbci.co.uk/sport/rss.xml",
            "https://www.theguardian.com/sport/rss",
        ],
    },
    "Entertainment": {
        "top_n": 10,
        "keywords": None,
        "feeds": [
            "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
            "https://www.theguardian.com/culture/rss",
        ],
    },
    "AI & Technology": {
        "top_n": 20,  # you asked for double the usual count here
        "keywords": None,
        "feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://venturebeat.com/category/ai/feed/",
            "https://www.wired.com/feed/rss",
            "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://www.theguardian.com/technology/rss",
        ],
    },
    "LLMs": {
        "top_n": 10,
        # Reuses the same AI-focused feeds as "AI & Technology" - the
        # distinction between the two categories is enforced by the
        # instruction given to Gemini in summarize.py (LLM model releases
        # specifically), not by a separate set of feeds.
        "keywords": None,
        "feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://venturebeat.com/category/ai/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.wired.com/feed/rss",
        ],
    },
}
