from typing import Union, List

from pydantic import BaseModel


class Slide(BaseModel):
    id: int
    pres_id: str
    index: int


class BuildPresentationModel(BaseModel):
    name: str
    save_to: str
    style_template: Union[None, str]
    ratio: str
    slides: List['Slide']