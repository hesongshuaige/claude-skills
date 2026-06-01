"""
Reddit Scraper using browser cookie authentication.
No API key needed - uses logged-in browser session.
Rate limit: ~100 requests / 10 minutes.
"""

import json
import requests
import time
import random
from pathlib import Path

STATE_FILE = "/tmp/reddit_state.json"

class RedditScraper:
    def __init__(self, state_file=STATE_FILE):
        self._normalize = lambda s: s.replace('r/', '', 1).strip() if s.startswith('r/') else s
        self.session = requests.Session()
        
        # Load browser cookies
        with open(state_file) as f:
            state = json.load(f)
        for c in state["cookies"]:
            self.session.cookies.set(
                c["name"], c["value"],
                domain=c.get("domain", ".reddit.com"),
                path=c.get("path", "/")
            )
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
        })
    
    def _get(self, url, params=None):
        """Rate-limited GET request."""
        r = self.session.get(url, params=params, timeout=15)
        if r.status_code == 429:
            print("Rate limited, waiting...")
            time.sleep(60)
            return self._get(url, params)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:200]}")
            return None
        return r.json()
    
    def hot_posts(self, subreddit, limit=25):
        """Get hot posts. Bare name or r/ prefix both OK."""
        subreddit = self._normalize(subreddit)
        posts = []
        after = None
        while len(posts) < limit:
            params = {"limit": min(100, limit - len(posts)), "raw_json": 1}
            if after:
                params["after"] = after
            
            data = self._get(f"https://oauth.reddit.com/r/{subreddit}/hot.json", params)
            if not data:
                break
            
            for child in data["data"]["children"]:
                d = child["data"]
                posts.append({
                    "title": d["title"],
                    "author": d["author"],
                    "score": d["score"],
                    "comments": d["num_comments"],
                    "url": f"https://reddit.com{d['permalink']}",
                    "created": d["created_utc"],
                    "subreddit": d["subreddit"],
                })
            
            after = data["data"].get("after")
            if not after:
                break
            time.sleep(random.uniform(1, 2))
        
        return posts[:limit]
    
    def search(self, query, subreddit=None, limit=25, sort="relevance"):
        """Search Reddit posts."""
        if subreddit:
            subreddit = self._normalize(subreddit)
            url = f"https://oauth.reddit.com/r/{subreddit}/search.json"
        else:
            url = "https://oauth.reddit.com/search.json"
        
        params = {"q": query, "limit": limit, "sort": sort, "type": "link", "restrict_sr": "on" if subreddit else "off"}
        data = self._get(url, params)
        
        if not data:
            return []
        
        results = []
        for child in data["data"]["children"]:
            d = child["data"]
            results.append({
                "title": d["title"],
                "author": d["author"],
                "score": d["score"],
                "url": f"https://reddit.com{d['permalink']}",
                "subreddit": d["subreddit"],
                "description": d.get("selftext", "")[:300],
            })
        return results
    
    def post_comments(self, permalink):
        """Get comments for a post."""
        url = f"https://oauth.reddit.com{permalink}.json"
        data = self._get(url)
        if not data:
            return []
        
        comments = []
        def extract(children):
            for child in children:
                if child["kind"] == "t1":
                    d = child["data"]
                    comments.append({
                        "author": d.get("author", "[deleted]"),
                        "body": d.get("body", ""),
                        "score": d.get("score", 0),
                    })
                    if d.get("replies") and isinstance(d["replies"], dict):
                        extract(d["replies"]["data"]["children"])
        
        if len(data) >= 2:
            extract(data[1]["data"]["children"])
        return comments


if __name__ == "__main__":
    scraper = RedditScraper()
    
    print("=== r/Python Hot Posts ===")
    for i, p in enumerate(scraper.hot_posts("Python", limit=5), 1):
        print(f"{i}. [{p['score']}pts] {p['title'][:80]}")
    
    print("\n=== Search: 'web scraping 2026' ===")
    for i, r in enumerate(scraper.search("web scraping 2026", limit=3), 1):
        print(f"{i}. [{r['score']}pts] r/{r['subreddit']} - {r['title'][:70]}")
