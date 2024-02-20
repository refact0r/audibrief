import asyncio
from random import random
import aiohttp
import os
from quart import Quart
from quart import request
from aiocache import cached
from quart_cors import cors
import feedparser
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import base64
import json

# load the environment variables from the .env file
load_dotenv()

# get environment variables
openai_key = os.getenv("OPENAI_API_KEY")
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")


# override Quart class to add aiohttp and openai clients
class QuartApp(Quart):
    aiohttp: aiohttp.ClientSession
    openai: openai.AsyncOpenAI

    def __init__(self, name):
        super().__init__(name)


# initialize quart server
app = QuartApp(__name__)
app = cors(app, allow_origin="*")


@app.before_serving
async def startup():
    app.aiohttp = aiohttp.ClientSession()
    app.openai = openai.AsyncOpenAI(api_key=openai_key)


@app.after_serving
async def cleanup():
    await app.aiohttp.close()


# root route: return generated audio from top 5 news articles from google news
@app.get("/")
async def root():
    articles = await getArticles()
    return {"articles": articles}


# custom route: return generated audio from custom article link
@app.post("/custom")
async def custom():
    data = await request.get_json()
    article = await getCustom(data["prompt"], data["link"])
    return article


# test route
@app.get("/test")
async def test():
    with open("result.json") as f:
        data = f.read()
    return json.loads(data)


# get top 5 news articles from google news
# cache results for 1 hour (because ai is slow and expensive)
@cached(ttl=3600)
async def getArticles():
    # get articles from google news rss feed
    url = "https://news.google.com/rss"
    feed = feedparser.parse(url)

    # loop through and crawl articles
    done = 0
    articles = []
    for entry in feed.entries:
        article = await crawlArticle(entry.link)

        # validate article is good
        if not article or len(article["content"]) < 200:
            continue

        articles.append(article)

        # stop after 5 valid articles
        done += 1
        if done == 5:
            break

    # generate audio for each article
    tasks = []
    for article in articles:
        task = asyncio.create_task(
            coro=generateSummary(
                "Summarize this news article with detail: ", article["content"]
            ),
        )
        tasks.append(task)

    # gather results from all tasks
    results = await asyncio.gather(*tasks, return_exceptions=False)
    for i in range(len(articles)):
        articles[i]["summary"] = results[i]
        articles[i].pop("content", None)

    # generate audio (can't be done in parallel because of api rate limits)
    for i in range(len(articles)):
        articles[i]["audio"] = await generateAudio(articles[i]["summary"])

    return articles


# get brief from custom prompt and link
# cache results for 1 hour (because ai is slow and expensive)
@cached(ttl=3600)
async def getCustom(prompt, link):
    # crawl article
    article = await crawlArticle(link)

    # validate article is good
    if not article or len(article["content"]) < 200:
        return {}

    # generate audio for each article
    article["summary"], article["audio"] = await generateAudio(
        prompt, article["content"]
    )
    article.pop("content", None)

    return article


# crawl an article and return its title, content, and link
# cache results for 1 hour
@cached(ttl=3600)
async def crawlArticle(link):
    print("crawling article: " + link)

    # send get request to article link
    response = await app.aiohttp.get(
        link, allow_redirects=True, headers={"User-Agent": "python-requests/2.31.0"}
    )
    print("redirect url: " + str(response.url))

    # parse html response with soup
    soup = BeautifulSoup(await response.text(), "html.parser")

    # get article title
    title = soup.title
    if title:
        title = title.string
    else:
        return None

    # collect article content
    content = ""
    for p in soup("h1") + soup("p"):
        content += p.get_text(strip=True) + "\n"

    return {"title": title, "content": content, "link": str(response.url)}


# generate summary from article content
# cache results for 1 hour
@cached(ttl=3600)
async def generateSummary(prompt, content):
    # get generated completion from openai
    completion = await app.openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt + "\n" + content,
            },
        ],
    )

    print(completion)
    print()

    # extract summary from completion response
    summary = completion.choices[0].message.content

    print(summary)
    print()

    return summary


# generate audio from summary
# cache results for 1 hour
@cached(ttl=3600)
async def generateAudio(summary):
    # id of "Alice" voice
    voiceId = "Xb7hH8MSUJpSbSDYk0k2"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voiceId}"
    # configure request
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
        "xi-api-key": elevenlabs_key,
        "Content-Type": "application/json",
    }
    # avoid overloading api
    await asyncio.sleep(random() * 4)
    # send request to elevenlabs
    response = await app.aiohttp.post(url, json=payload, headers=headers)

    print(response)

    # save audio to file (FOR TESTING)
    # CHUNK_SIZE = 1024
    # with open(f"{content[0:10]}.mp3", "wb") as f:
    #     while True:
    #         chunk = await response.content.read(CHUNK_SIZE)
    #         if not chunk:
    #             break
    #         f.write(chunk)

    # encode audio to base64
    data = await response.content.read()
    base64_audio = base64.b64encode(data).decode("utf-8")

    # save audio to text file (FOR TESTING)
    # with open(f"{content[0:10]}.txt", "wb") as f:
    #     f.write(base64_audio.encode("utf-8"))

    return base64_audio


app.run()
