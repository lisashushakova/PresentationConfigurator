from typing import List

from pydantic import BaseModel


class Presentation(BaseModel):
    id: str
    name: str

class FilterModel(BaseModel):
    presentations: List['Presentation']
    tag_query: str
    text_phrase: str
    ratio: str