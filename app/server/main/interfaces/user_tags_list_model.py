from typing import List

from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    name: str
    owner_id: str


class UserTagsListModel(BaseModel):
    presentations_tags: List['Tag']
    slides_tags: List['Tag']