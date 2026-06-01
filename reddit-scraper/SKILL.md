---
name: reddit-scraper
description: Scrape Reddit. Use when the user asks for Reddit data, hot posts, subreddit content, Reddit search, Reddit comments, Reddit trends, or anything from Reddit. Triggered by mentions of Reddit, r/, subreddit, Reddit scraping, Reddit API.
---

# Reddit Scraper

Cookie-authenticated Reddit JSON API. No keys. Rate limit: ~100 req / 10 min.

## When NOT to use

If the user wants to POST, comment, vote, or modify Reddit — this is read-only. Say "我只能读，不能发帖或互动。"

## Pre-flight

State file at `/tmp/reddit_state.json` MUST exist. To verify and handle missing:

```bash
if [ ! -f /tmp/reddit_state.json ]; then
  echo "STATE_MISSING"
fi
```

If STATE_MISSING: tell the user "Reddit Cookie 已过期，需要重新登录。运行 `invisible_playwright` 登录后导出 state。" Do NOT attempt to scrape without it.

## Defaults for ambiguous queries

| User says | Do |
|-----------|----|
| "Reddit 热帖" / "what's hot" | `hot_posts("all", limit=10)` |
| "看看 Reddit" / no subreddit specified | `hot_posts("all", limit=10)` |
| Mentions a topic but no subreddit | `search("topic", limit=10)` |

## How to run

Always run from the skill's `scripts/` directory:

```bash
cd /home/ubuntu/.agents/skills/reddit-scraper/scripts && python3 << 'PYEOF'
from reddit_scraper import RedditScraper
s = RedditScraper()
# ... calls here ...
PYEOF
```

Do NOT use `$(dirname "$0")` — use the absolute path above.

## API reference

```python
from reddit_scraper import RedditScraper
s = RedditScraper()

# Hot posts — bare name or r/ prefix both OK
s.hot_posts("Python", limit=25)
# → [{title, author, score, comments, url, created, subreddit}, ...]

# Search — subreddit is optional
s.search("query", subreddit=None, limit=25, sort="relevance")
# sort: "relevance" | "new" | "top" | "comments"

# Comments on a post — use full permalink path
s.post_comments("/r/Python/comments/abc123/title/")
# → [{author, body, score}, ...]
```

## Output rules

After every successful call, present results as a numbered list:
```
1. [score pts] Title text
2. [score pts] Title text
```

If 0 results: say "没有找到相关内容。"

## Error handling

| Status | Meaning | Action |
|--------|---------|--------|
| 403 | IP blocked | Tell user "服务器 IP 被 Reddit 封锁，需要代理。" Stop. |
| 429 | Rate limited | Script auto-retries with backoff. Do nothing extra. |
| 404 | Not found | If subreddit: tell user "r/xxx 不存在或已设为私有。" If post: tell user "帖子不存在或已删除。" |
| Cookie expired | Nov 2026 | Tell user "Cookie 已过期，需重新登录。" |

## Forbidden

- Never modify `/tmp/reddit_state.json`
- Never hardcode credentials in scripts
- Never attempt write operations (post, comment, vote)
- Never scrape faster than 1 request/second (script handles this)
