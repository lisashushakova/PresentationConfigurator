from typing import List

from pydantic import BaseModel


class SlideModel(BaseModel):
    id: int
    index: int
    pres_id: str


class PresentationModel(BaseModel, object):
    id: str
    slides: List[SlideModel]


class BuildPresentationModel(BaseModel):
    name: str
    build_from: List[SlideModel]
