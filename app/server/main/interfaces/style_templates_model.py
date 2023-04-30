from typing import List

from pydantic import BaseModel


class StyleTemplate(BaseModel):
    id: str
    thumbnail: str


class StyleTemplatesModel(BaseModel):
    templates: List['StyleTemplate']