from mirascope.core import cohere, prompt_template
from pydantic import BaseModel, ConfigDict, Field


class Book(BaseModel):
    title: str = Field(..., examples=["THE NAME OF THE WIND"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
            ]
        }
    )


@cohere.call("command-r-plus", response_model=Book, json_mode=True)
@prompt_template("Extract {text}. Match example format excluding 'examples' key.")
def extract_book(text: str): ...


book = extract_book("The Way of Kings by Brandon Sanderson")
print(book)
# Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
