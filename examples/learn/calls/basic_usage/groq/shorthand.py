from mirascope.core import groq


@groq.call("llama-3.1-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))