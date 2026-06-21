"""
fetch_news.py
-------------
Pulls headlines published in the last N hours from a list of RSS feeds.

Why RSS instead of a paid news API:
- Free, no API key required (the option you picked).
- We're pulling directly from each outlet's own feed (BBC, Guardian, Al
  Jazeera, NPR, TechCrunch, etc.) rather than a re-packaged aggregator,
  so "reputable source" is enforced by which feeds are in config.py, not
  just by asking the LLM nicely.
- Tradeoff: RSS only carries headline + short summary, not full article
  text. That's fine here - Gemini ranks/summarizes from those snippets
  and the email links out to the original article for anyone who wants
  the full story.
"""

import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AINewsDigest/1.0; +https://github.com/)"
}
REQUEST_TIMEOUT = 10  # seconds - one slow feed shouldn't stall the whole run


def _parse_published(entry):
    """Return a timezone-aware UTC datetime for an entry, or None if absent."""
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not time_struct:
        return None
    return datetime.fromtimestamp(time.mktime(time_struct), tz=timezone.utc)


def fetch_recent_entries(feed_urls, hours=24):
    """
    Fetch entries from a list of RSS feed URLs published within the last
    `hours` hours. Returns a de-duplicated list of dicts:
    {title, link, summary, source, published}
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seen_links = set()
    entries = []

    for url in feed_urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
        except Exception as exc:
            # A dead/renamed feed shouldn't kill the whole digest.
            print(f"[fetch_news] Skipping {url}: {exc}")
            continue

        source_name = parsed.feed.get("title", url)

        for item in parsed.entries:
            published = _parse_published(item)
            # If a feed doesn't expose a timestamp we keep the item rather
            # than dropping it silently - better a slightly-stale headline
            # than missing a major story over a formatting quirk.
            if published is not None and published < cutoff:
                continue

            link = item.get("link", "")
            if link and link in seen_links:
                continue
            if link:
                seen_links.add(link)

            entries.append({
                "title": item.get("title", "").strip(),
                "link": link,
                "summary": item.get("summary", "")[:500],  # keep prompt size sane
                "source": source_name,
                "published": published.isoformat() if published else "unknown",
            })

    return entries


def filter_by_keywords(entries, keywords):
    """Keep only entries whose title or summary mentions one of `keywords`.
    Used for the 'Wars & Conflicts' category to pull conflict stories out
    of the general world-news feeds. Pass keywords=None to skip filtering."""
    if not keywords:
        return entries
    lowered = [k.lower() for k in keywords]
    filtered = []
    for entry in entries:
        text = f"{entry['title']} {entry['summary']}".lower()
        if any(k in text for k in lowered):
            filtered.append(entry)
    return filtered
