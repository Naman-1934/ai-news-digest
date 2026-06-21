# Your World Digest

An automated agent that emails you a daily news briefing at **9:00 AM IST**,
covering the last 24 hours, summarized into 400-500 words per category:

- World & Politics — top 10
- Wars & Conflicts (Russia-Ukraine, Israel-Gaza, US-Iran, and any other
  active flashpoint) — top 10
- Business & Economy — top 10
- Science — top 10
- Health — top 10
- Sports — top 10
- Entertainment — top 10
- **AI & Technology — top 20**, strictly AI tools/products launched or
  majorly updated in the last 24 hours
- **LLMs — top 10**, strictly new large language models launched or
  majorly updated in the last 24 hours

## How it works (and why it's built this way)

```
GitHub Actions (cron, 9:00 AM IST daily)
        │
        ▼
  main.py
        │
        ├─► fetch_news.py   → pulls RSS from BBC, Guardian, Al Jazeera,
        │                      NPR, TechCrunch, The Verge, etc. (free,
        │                      no API key, last 24h only)
        │
        ├─► summarize.py    → sends each category's headlines to Gemini,
        │                      which picks the top N and writes the
        │                      400-500 word summary
        │
        └─► send_email.py   → emails the finished digest to you via
                               Gmail SMTP
```

**Why GitHub Actions instead of your own laptop:** a scheduled task only
fires if your machine is on, awake, and online at that exact moment. GitHub
Actions runs in the cloud independent of your laptop, so the 9 AM email
arrives whether your PC is on or not. It's free for a job this small.

**Why RSS instead of a paid news API:** no signup, no API key, no cost —
and you're pulling directly from each outlet's own feed rather than a
re-packaged aggregator, so "reputable source" is enforced by which feeds
are listed in `src/config.py`, not just by asking the LLM nicely.

## One-time setup

You'll need three things: a GitHub account, a Gemini API key, and a Gmail
account you're willing to send from.

### 1. Get a Gemini API key

1. Go to [aistudio.google.com](https://aistudio.google.com/apikey)
2. Sign in, click **Create API key**, copy it somewhere safe.

### 2. Create a Gmail "App Password"

Gmail won't accept your normal password for a script like this — you need
a dedicated App Password.

1. On the sending Gmail account, turn on **2-Step Verification**
   (Google Account → Security → 2-Step Verification).
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create one for "Mail" / "Other (Custom name)" → name it `world-digest`.
4. Copy the 16-character password it generates — you'll only see it once.

### 3. Push this code to GitHub

```bash
cd ai-news-digest
git add -A
git commit -m "Initial commit: daily world digest agent"
```

Create a new (can be private) repo on GitHub, then:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

### 4. Add your secrets to GitHub

In your new repo: **Settings → Secrets and variables → Actions → New
repository secret**. Add all four:

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | the key from step 1 |
| `SENDER_EMAIL` | the Gmail address sending the digest |
| `SENDER_APP_PASSWORD` | the 16-character app password from step 2 |
| `RECEIVER_EMAIL` | the email address you want to receive it at (can be the same as `SENDER_EMAIL`) |

### 5. Test it manually before trusting the schedule

Repo → **Actions tab** → "Daily World Digest" workflow → **Run workflow**
button → Run. Watch the logs; check your inbox a minute or two later. This
button is there permanently, so you can always trigger a digest on demand.

From here, it runs automatically every day at 9:00 AM IST — nothing more
to do.

## (Optional) Test locally first on your own machine

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in your real values in .env
python main.py
```

## Customizing it

- **Change which time it sends:** edit the `cron` line in
  `.github/workflows/daily-digest.yml`. GitHub Actions cron is always UTC
  — IST is UTC+5:30, so subtract 5:30 from your desired IST time.
- **Add/remove a category, change top_n, change feeds:** everything lives
  in `src/config.py` — no other file needs to change.
- **Add another RSS feed to an existing category:** just append its URL
  to that category's `feeds` list in `src/config.py`.
- **Swap the Gemini model:** one line — `MODEL_NAME` at the top of
  `src/summarize.py`.

## Known limitations

- The 400-500 word target is a strong instruction to Gemini, not a hard
  guarantee — LLMs are approximate at exact word counts.
- GitHub Actions' free-tier cron can run a few minutes late during high
  load; it's not millisecond-precise.
- RSS feed URLs occasionally change if an outlet redesigns its site. If a
  category starts coming back empty, check the feed URLs in
  `src/config.py` still resolve.
- If a category has zero qualifying stories in the last 24 hours (rare,
  but possible for something like "Wars & Conflicts" on a quiet day),
  the digest says so plainly instead of fabricating content.
