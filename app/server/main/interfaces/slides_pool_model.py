from typing import List

from pydantic import BaseModel


class Slide(BaseModel):
    id: int
    pres_id: str

class SlidesPoolModel(BaseModel):
    slides: List['Slide']
