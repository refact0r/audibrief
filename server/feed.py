import feedparser
import openai
from pathlib import Path

url = "http://feeds.feedburner.com/TheAtlantic"

feed = feedparser.parse(url)

content = feed.entries[0].content[0].value

print(content)
print()

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

speech_file_path = Path(__file__).parent / "speech.mp3"
with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=summary,  # type: ignore
    response_format="mp3",
) as response:
    response.stream_to_file(speech_file_path)
