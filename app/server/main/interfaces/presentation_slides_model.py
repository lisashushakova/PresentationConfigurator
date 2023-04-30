from typing import List

from pydantic import BaseModel


class Slide(BaseModel):
    id: int
    pres_id: str
    index: int
    thumbnail: str
    ratio: List[str]
    text: str

class PresentationSlidesModel(BaseModel):
    slides: List['Slide']
