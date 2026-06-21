"""
main.py
-------
Entry point. Run this directly (`python main.py`) to fetch, summarize, and
email today's digest. This is exactly what the GitHub Actions workflow
(.github/workflows/daily-digest.yml) runs automatically every day at
9:00 AM IST.
"""

from dotenv import load_dotenv

# No-op when running in GitHub Actions (no .env file exists there - the
# workflow injects secrets as real environment variables instead). Loads
# your local .env automatically when you test on your own machine.
load_dotenv()

from src.config import CATEGORIES
from src.fetch_news import fetch_recent_entries, filter_by_keywords
from src.summarize import summarize_category
from src.send_email import send_digest


def build_digest():
    sections = {}
    for category, cfg in CATEGORIES.items():
        print(f"[main] Fetching: {category}")
        entries = fetch_recent_entries(cfg["feeds"], hours=24)
        entries = filter_by_keywords(entries, cfg.get("keywords"))
        print(f"[main]   {len(entries)} candidate stories found")

        print(f"[main] Summarizing: {category}")
        sections[category] = summarize_category(category, entries, cfg["top_n"])

    return sections


def main():
    sections = build_digest()
    send_digest(sections)
    print("[main] Done.")


if __name__ == "__main__":
    main()
