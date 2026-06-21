"""
summarize.py
------------
Sends the raw RSS entries for ONE category to Gemini and asks it to pick
the most important ones and write a single combined 400-500 word summary.

Why per-category calls instead of one giant prompt with everything: each
category gets a focused instruction (e.g. "AI & Technology" explicitly
asks for newly launched models/tools over general commentary), and a
failure on one category's API call doesn't take down the whole digest.
"""

import json
import os

from google import genai

# Current GA (production-ready) Gemini Flash model as of mid-2026.
# If Google renames or retires this model later, update this one string -
# nothing else in the file needs to change.
MODEL_NAME = "gemini-3.5-flash"

PROMPT_TEMPLATE = """You are a professional news editor producing a daily briefing.

Category: {category}
Time window: last 24 hours

Below is a JSON list of candidate news items from reputable outlets. Each item has a title, source, link, and a short raw summary.

Your task:
1. Select the {top_n} most significant, high-impact, genuinely newsworthy items. Skip duplicates covering the same underlying event - pick the single best version of that story.
2. {category_instruction}
3. Write the result as a numbered list from 1 to {top_n}. Each entry should be 2-4 sentences in your own words covering what happened and why it matters, followed by "Source: <source name>" on its own line.
4. The combined word count of ALL {top_n} entries together must be between 400 and 500 words. Be precise and substantive - don't pad with filler to hit the count.
5. Output ONLY the numbered list. No preamble, no closing remarks, no markdown headers.

Candidate items:
{items_json}
"""

CATEGORY_INSTRUCTIONS = {
    "AI & Technology": (
        "Focus strictly on AI tools and AI products that were launched, "
        "released, or had a major update announced in the last 24 hours. "
        "Skip general tech commentary, opinion pieces, and non-AI tech "
        "news entirely - if there aren't enough genuine AI-tool-launch "
        "stories to fill the list, include the strongest AI-adjacent tech "
        "news instead of padding with unrelated stories."
    ),
    "LLMs": (
        "Focus strictly on new large language models (LLMs) that were "
        "launched, released, or had a major version update announced in "
        "the last 24 hours - e.g. new models from labs like OpenAI, "
        "Google DeepMind, Anthropic, Meta, Mistral, xAI, DeepSeek, or "
        "any other lab. Skip general AI tool news that isn't about an "
        "LLM release itself."
    ),
    "Wars & Conflicts": (
        "Cover the most significant developments across ALL active "
        "conflicts and geopolitical flashpoints worldwide (e.g. Russia-"
        "Ukraine, Israel-Gaza, US-Iran tensions, and others) - don't let "
        "one conflict crowd out the others if multiple had developments "
        "in the last 24 hours."
    ),
}
DEFAULT_INSTRUCTION = "Prioritize stories with the broadest global impact."


def summarize_category(category, entries, top_n):
    """Return a Gemini-written digest string for one category, or a
    fallback plain-text list if the API call fails for any reason."""
    if not entries:
        return "No qualifying stories were found in the last 24 hours for this category."

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)

        # Cap candidates sent to the model - keeps the prompt small and
        # cheap while still giving Gemini plenty to choose the best from.
        candidates = entries[: max(top_n * 4, 30)]

        prompt = PROMPT_TEMPLATE.format(
            category=category,
            top_n=top_n,
            category_instruction=CATEGORY_INSTRUCTIONS.get(category, DEFAULT_INSTRUCTION),
            items_json=json.dumps(candidates, ensure_ascii=False, indent=2),
        )

        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip()
    except Exception as exc:
        print(f"[summarize] Gemini call failed for {category}: {exc}")
        # Fallback so the email still goes out even if Gemini is down (or
        # the API key is missing/invalid) - raw headlines instead of a
        # polished summary.
        fallback_lines = [
            f"{i+1}. {e['title']} (Source: {e['source']}) - {e['link']}"
            for i, e in enumerate(entries[:top_n])
        ]
        return "\n".join(fallback_lines)
