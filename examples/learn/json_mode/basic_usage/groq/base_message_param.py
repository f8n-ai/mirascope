import json

from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.1-70b-versatile", json_mode=True)
def get_book_info(book_title: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Provide the author and genre of {book_title}"
        )
    ]


response = get_book_info("The Name of the Wind")
print(json.loads(response.content))
# Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
