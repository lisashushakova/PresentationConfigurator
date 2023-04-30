from typing import List

from pydantic import BaseModel


class SlideModel(BaseModel):
    id: int
    pres_id: str
    index: int
    text: str
    thumbnail: str
    ratio: str
    label: str

class FilteredSlidesModel(BaseModel):
    slides: List['SlideModel']