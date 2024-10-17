import asyncio
from typing import Any, Callable

from mirascope.beta.openai import Context, Realtime, async_input

from mirascope.beta.openai import OpenAIRealtimeTool

app = Realtime(
    "gpt-4o-realtime-preview-2024-10-01",
    modalities=["text"],
)


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@app.sender(wait_for_text_response=True)
async def send_message(context: Context) -> tuple[str, Callable]:
    genre = await async_input("Enter a genre: ")
    return f"Recommend a {genre} book", format_book


@app.receiver("text")
async def receive_text(response: str, context: dict[str, Any]) -> None:
    print(f"AI(text): {response}", flush=True)


@app.receiver("tool")
async def recommend_book(response: OpenAIRealtimeTool, context: Context) -> None:
    print(response.call())


asyncio.run(app.run())
