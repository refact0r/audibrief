import requests
import feedparser
import openai
from bs4 import BeautifulSoup
from pathlib import Path

url = "http://www.npr.org/rss/rss.php?id=1001"

feed = feedparser.parse(url)

link = feed.entries[0].link

print(link)

eleven_response = requests.get(link)

soup = BeautifulSoup(eleven_response.text, "html.parser")

content = ""

for p in soup("h1") + soup("p"):
    content += p.get_text(strip=True) + "\n"

print(content)

client = openai.OpenAI(api_key="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")

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "Summarize this news article with detail: " + content,
        },
    ],
)

print(completion)
print()

summary = completion.choices[0].message.content

print(summary)

url = "https://api.elevenlabs.io/v1/text-to-speech/Xb7hH8MSUJpSbSDYk0k2"

payload = {
    "model_id": "eleven_turbo_v2",
    "text": summary,
    "voice_settings": {
        "similarity_boost": 0.5,
        "stability": 0.75,
        "style": 0,
        "use_speaker_boost": True,
    },
}
headers = {
    "xi-api-key": "302cd538e666de491d77b1cc388c8a20",
    "Content-Type": "application/json",
}

eleven_response = requests.request("POST", url, json=payload, headers=headers)

CHUNK_SIZE = 1024
with open("output.mp3", "wb") as f:
    for chunk in eleven_response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)
