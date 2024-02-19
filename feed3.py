import requests
import feedparser
import openai
from bs4 import BeautifulSoup
from pathlib import Path

url = "https://news.google.com/rss"

feed = feedparser.parse(url)

for link in feed.entries:
    print(link)
    response = requests.get(link)

    if response.history:
        print("Request was redirected")
        for resp in response.history:
            print(resp.status_code, resp.url)
        print("Final destination:")
        print(response.status_code, response.url)
    else:
        print("Request was not redirected")

eleven_response = requests.get(link)

soup = BeautifulSoup(eleven_response.text, "html.parser")

content = ""

for p in soup("h1") + soup("p"):
    content += p.get_text(strip=True) + "\n"

print(content)
