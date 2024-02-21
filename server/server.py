import asyncio
from random import random
import time
import aiohttp
import os
from quart import Quart, make_response
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


# setup aiohttp and openai clients
@app.before_serving
async def startup():
    app.aiohttp = aiohttp.ClientSession()
    app.openai = openai.AsyncOpenAI(api_key=openai_key)


# close aiohttp client when server stops
@app.after_serving
async def cleanup():
    await app.aiohttp.close()


# root route: return generated audio from top 5 news articles from google news
@app.get("/")  # type: ignore
async def root():
    return async_generator_openai()


# custom route: return generated audio from custom article link
@app.post("/custom")
async def custom():
    data = await request.get_json()
    article = await getCustom(data["prompt"], data["link"])
    return article


# test route
@app.get("/example")
async def example():
    with open("result.json") as f:
        data = f.read()
    return json.loads(data)


# root route async generator to stream audio results (from elevenlabs)
async def async_generator():
    yield '{"articles": ['.encode()

    # get articles from google news rss feed
    articles = await getArticles()

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

    # create new articles (using the old articles reference will alter the cached articles)
    new_articles = []
    for i in range(len(articles)):
        new_articles.append(
            {
                "title": articles[i]["title"],
                "link": articles[i]["link"],
                "summary": results[i],
            }
        )

    # generate audio (can't be done in parallel because of api rate limits)
    for i in range(len(new_articles)):
        new_articles[i]["audio"] = await generateAudio(new_articles[i]["summary"])
        yield (
            json.dumps(new_articles[i]) + (", " if i < len(new_articles) - 1 else "")
        ).encode()

    yield "]}".encode()


# root route async generator to stream audio results (from openai)
async def async_generator_openai():
    yield '{"articles": '.encode()

    # get articles from google news rss feed
    articles = await getArticles()

    # create tasks to generate summary and audio for each article
    tasks = []
    for i in range(len(articles)):
        task = asyncio.create_task(coro=generateSummaryAndAudio(articles[i]))
        tasks.append(task)

    # gather results from all tasks
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # create new articles (using the old articles reference will alter the cached articles)
    new_articles = []
    for i in range(len(articles)):
        new_articles.append(
            {
                "title": articles[i]["title"],
                "link": articles[i]["link"],
                "summary": results[i][0],
                "audio": results[i][1],
            }
        )

    yield json.dumps(new_articles).encode()

    yield "}".encode()


# get summary and audio for article in sequence
@cached(ttl=3600)
async def generateSummaryAndAudio(article):
    # generate summary for article
    summary = await generateSummary(
        "Summarize this news article with detail: ", article["content"]
    )

    # generate audio for summary
    audio = await generateAudioOpenAI(summary)

    return (summary, audio)


# fetch, crawl, and parse articles from google news rss feed
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
        if not article or "content" not in article or len(article["content"]) < 200:
            continue

        articles.append(article)

        # stop after 5 valid articles
        done += 1
        if done == 5:
            break

    return articles


async def fakeArticles():
    return [
        {"title": "title1", "link": "link1", "content": "content1"},
        {"title": "title2", "link": "link2", "content": "content2"},
    ]


# get audio from custom prompt and link
@cached(ttl=3600)
async def getCustom(prompt, link):
    # crawl article
    article = await crawlArticle(link)

    # validate article is good
    if not article or len(article["content"]) < 200:
        return {}

    # generate audio for each article
    article["summary"], article["audio"] = await generateAudio(
        prompt, article["content"], 0
    )
    article.pop("content", None)

    return article


# crawl an article and return its title, content, and link
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

    # extract summary from completion response
    summary = completion.choices[0].message.content

    print(summary)
    print()

    return summary


async def fakeSummary(prompt, content):
    return "summary"


# generate audio from summary (elevenlabs)
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


# generate audio from summary (openai)
@cached(ttl=3600)
async def generateAudioOpenAI(summary):
    # get audio from openai
    response = await app.openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=summary,
        response_format="mp3",
    )

    # encode audio to base64
    base64_audio = base64.b64encode(response.content).decode("utf-8")

    return base64_audio


async def fakeAudio(summary):
    return "audio"
