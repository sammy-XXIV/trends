from flask import Flask, render_template_string
import feedparser
import requests
from datetime import datetime
import time

app = Flask(__name__)

FEEDS = {
    "Google News — Kash Patel": "https://news.google.com/rss/search?q=Kash+Patel&hl=en-US&gl=US&ceid=US:en",
    "Google News — FBI Director": "https://news.google.com/rss/search?q=FBI+Director+Patel&hl=en-US&gl=US&ceid=US:en",
    "Google News — Epstein FBI": "https://news.google.com/rss/search?q=Epstein+FBI+Patel&hl=en-US&gl=US&ceid=US:en",
    "Google News — Pete Hegseth": "https://news.google.com/rss/search?q=Pete+Hegseth+Senate&hl=en-US&gl=US&ceid=US:en",
    "Google News — Pam Bondi": "https://news.google.com/rss/search?q=Pam+Bondi+Senate&hl=en-US&gl=US&ceid=US:en",
    "The Hill": "https://thehill.com/rss/syndicator/19109",
    "Axios Politics": "https://api.axios.com/feed/politics",
    "CBS News Politics": "https://www.cbsnews.com/latest/rss/politics",
}

KEYWORDS = [
    "patel", "hegseth", "bondi", "epstein", "fbi", "senate", "hearing",
    "congress", "booker", "whitehouse", "swalwell", "massie", "schiff",
    "van hollen", "lieu", "judiciary", "appropriations", "intelligence"
]

def fetch_articles():
    articles = []
    seen = set()
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                pub = entry.get("published", "")
                summary = entry.get("summary", "")

                if title in seen:
                    continue
                if title.startswith("http") or len(title) > 200:
                    continue

                text = (title + " " + summary).lower()
                if not any(kw in text for kw in KEYWORDS):
                    continue

                seen.add(title)

                try:
                    pub_dt = datetime(*entry.published_parsed[:6])
                    pub_str = pub_dt.strftime("%b %d, %Y — %I:%M %p")
                    pub_ts = pub_dt.timestamp()
                except:
                    pub_str = pub
                    pub_ts = 0

                articles.append({
                    "title": title,
                    "link": link,
                    "source": source,
                    "pub": pub_str,
                    "pub_ts": pub_ts,
                    "summary": summary[:200].strip() if summary else ""
                })
        except Exception as e:
            continue

    articles.sort(key=lambda x: x["pub_ts"], reverse=True)
    return articles

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="3600">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>.</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #000;
    color: #fff;
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    min-height: 100vh;
    padding: 24px 16px;
    max-width: 900px;
    margin: 0 auto;
    transition: background 0.2s, color 0.2s;
  }
  body.light {
    background: #fff;
    color: #000;
  }
  body.light .header { border-bottom-color: #000; }
  body.light .header-right { color: #999; }
  body.light .count { color: #bbb; }
  body.light .article { border-bottom-color: #eee; }
  body.light .article:hover { background: #f9f9f9; }
  body.light .source { color: #aaa; }
  body.light .pub { color: #ccc; }
  body.light .summary { color: #aaa; }
  body.light .tag { border-color: #ddd; color: #bbb; }
  body.light .section-label { color: #bbb; border-top-color: #eee; }
  body.light .trend-block { border-color: #eee; }
  body.light .trend-name { color: #aaa; }
  body.light .refresh-note { color: #ddd; }
  body.light iframe { filter: grayscale(1); opacity: 0.8; }
  .mode-toggle {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 11px;
    letter-spacing: 2px;
    background: none;
    border: 1px solid currentColor;
    color: inherit;
    padding: 4px 10px;
    cursor: pointer;
    opacity: 0.4;
  }
  .mode-toggle:hover { opacity: 1; }
  .header {
    border-bottom: 1px solid #fff;
    padding-bottom: 16px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 8px;
  }
  .header-left {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 40px;
    letter-spacing: 4px;
  }
  .header-right {
    font-size: 10px;
    color: #666;
    text-align: right;
    line-height: 1.8;
  }
  .count {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 12px;
    letter-spacing: 2px;
    color: #444;
    margin-bottom: 20px;
  }
  .article {
    border-bottom: 1px solid #1a1a1a;
    padding: 20px 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .article:hover { background: #0a0a0a; }
  .meta-row {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }
  .source {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    color: #555;
  }
  .pub {
    font-size: 10px;
    color: #333;
  }
  .content a {
    text-decoration: none;
    color: inherit;
  }
  .title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
    letter-spacing: 1px;
    line-height: 1.2;
    margin-top: 4px;
    word-break: break-word;
    overflow-wrap: break-word;
  }
  .title:hover { color: #ccc; }
  .summary {
    font-size: 12px;
    color: #555;
    line-height: 1.7;
    margin-top: 4px;
  }
  .tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
  .tag {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 9px;
    letter-spacing: 2px;
    border: 1px solid #222;
    padding: 2px 6px;
    color: #333;
  }
  .section-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 12px;
    letter-spacing: 3px;
    color: #444;
    margin-top: 50px;
    margin-bottom: 20px;
    border-top: 1px solid #1a1a1a;
    padding-top: 20px;
  }
  .trends-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 50px;
  }
  @media (max-width: 600px) {
    .trends-grid { grid-template-columns: 1fr; }
    .header-left { font-size: 32px; }
    .title { font-size: 18px; }
  }
  .trend-block {
    border: 1px solid #1a1a1a;
    padding: 12px;
  }
  .trend-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 12px;
    letter-spacing: 3px;
    color: #555;
    margin-bottom: 10px;
  }
  iframe {
    filter: invert(1) grayscale(1);
    opacity: 0.7;
    width: 100%;
  }
  .refresh-note {
    margin-top: 60px;
    font-size: 10px;
    color: #222;
    letter-spacing: 2px;
    font-family: 'Bebas Neue', sans-serif;
    text-align: center;
  }
  .tag {
    display: inline-block;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 9px;
    letter-spacing: 2px;
    border: 1px solid #222;
    padding: 2px 6px;
    color: #333;
    margin-top: 8px;
  }
</style>
</head>
<body>
<div class="header">
  <div class="header-left">TRENDING NOW</div>
  <div class="header-right">
    REFRESHES HOURLY<br>
    {{ now }}<br><br>
    <button class="mode-toggle" onclick="toggleMode()">LIGHT / DARK</button>
  </div>
</div>

<div class="count">{{ articles|length }} STORIES TRACKED</div>

{% for a in articles %}
<div class="article">
  <div class="meta-row">
    <div class="source">{{ a.source.split('—')[-1].strip() }}</div>
    <div class="pub">{{ a.pub }}</div>
  </div>
  <a href="{{ a.link }}" target="_blank">
    <div class="title">{{ a.title }}</div>
  </a>
  {% if a.summary %}
  <div class="summary">{{ a.summary }}...</div>
  {% endif %}
  <div class="tags">
    {% if 'patel' in a.title.lower() %}<span class="tag">PATEL</span>{% endif %}
    {% if 'epstein' in a.title.lower() %}<span class="tag">EPSTEIN</span>{% endif %}
    {% if 'hegseth' in a.title.lower() %}<span class="tag">HEGSETH</span>{% endif %}
    {% if 'bondi' in a.title.lower() %}<span class="tag">BONDI</span>{% endif %}
    {% if 'booker' in a.title.lower() %}<span class="tag">BOOKER</span>{% endif %}
    {% if 'senate' in a.title.lower() %}<span class="tag">SENATE</span>{% endif %}
  </div>
</div>
{% endfor %}

<div class="section-label">SEARCH MOMENTUM — LAST 7 DAYS</div>

<div class="trends-grid">
  <div class="trend-block">
    <div class="trend-name">KASH PATEL</div>
    <iframe src="https://trends.google.com/trends/embed/explore/TIMESERIES?req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22Kash%20Patel%22%2C%22geo%22%3A%22US%22%2C%22time%22%3A%22now%207-d%22%7D%5D%2C%22category%22%3A0%2C%22property%22%3A%22%22%7D&tz=-300" width="100%" height="200" frameborder="0" scrolling="0"></iframe>
  </div>
  <div class="trend-block">
    <div class="trend-name">EPSTEIN FILES</div>
    <iframe src="https://trends.google.com/trends/embed/explore/TIMESERIES?req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22Epstein%20files%22%2C%22geo%22%3A%22US%22%2C%22time%22%3A%22now%207-d%22%7D%5D%2C%22category%22%3A0%2C%22property%22%3A%22%22%7D&tz=-300" width="100%" height="200" frameborder="0" scrolling="0"></iframe>
  </div>
  <div class="trend-block">
    <div class="trend-name">PETE HEGSETH</div>
    <iframe src="https://trends.google.com/trends/embed/explore/TIMESERIES?req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22Pete%20Hegseth%22%2C%22geo%22%3A%22US%22%2C%22time%22%3A%22now%207-d%22%7D%5D%2C%22category%22%3A0%2C%22property%22%3A%22%22%7D&tz=-300" width="100%" height="200" frameborder="0" scrolling="0"></iframe>
  </div>
  <div class="trend-block">
    <div class="trend-name">PAM BONDI</div>
    <iframe src="https://trends.google.com/trends/embed/explore/TIMESERIES?req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22Pam%20Bondi%22%2C%22geo%22%3A%22US%22%2C%22time%22%3A%22now%207-d%22%7D%5D%2C%22category%22%3A0%2C%22property%22%3A%22%22%7D&tz=-300" width="100%" height="200" frameborder="0" scrolling="0"></iframe>
  </div>
</div>

<div class="refresh-note">AUTO REFRESH — EVERY 60 MINUTES</div>

<script>
  function toggleMode() {
    const isLight = document.body.classList.toggle('light');
    localStorage.setItem('mode', isLight ? 'light' : 'dark');
  }
  (function() {
    if (localStorage.getItem('mode') === 'light') {
      document.body.classList.add('light');
    }
  })();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    articles = fetch_articles()
    now = datetime.now().strftime("%B %d, %Y — %I:%M %p")
    return render_template_string(HTML, articles=articles, now=now)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
