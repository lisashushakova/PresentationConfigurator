from typing import Union, List

from pydantic import BaseModel


class SlideLink(BaseModel):
    link_id: int
    slide_id: int
    tag_id: int
    tag_name: str
    value: Union[int, None]


class PresentationLink(BaseModel):
    link_id: int
    presentation_id: str
    tag_id: int
    tag_name: str
    value: Union[int, None]


class TagListModel(BaseModel):
    links: Union[List['SlideLink'], List['PresentationLink']]
