from datetime import datetime
from quart import Quart
from quart import request
from cachetools import cached, TTLCache
import requests
import feedparser
import openai
from bs4 import BeautifulSoup
from pathlib import Path

app = Quart(__name__)


@app.post("/")
async def root():
    data = await request.get_json()
    return getArticles()


@cached(cache=TTLCache(maxsize=1, ttl=600))
def getArticles():
    url = "https://news.google.com/rss"
    feed = feedparser.parse(url)
    done = 0
    articles = []
    for entry in feed.entries:
        print(entry.link)
        response = requests.get(entry.link)
        print(response.url)
        soup = BeautifulSoup(response.text, "html.parser")
        content = ""
        for p in soup("h1") + soup("p"):
            content += p.get_text(strip=True) + "\n"
        if len(content) > 200:
            done += 1
        else:
            continue
        articles.append(
            {"title": entry.title, "content": content, "link": response.url}
        )
        if done == 5:
            break

    return articles


app.run()
