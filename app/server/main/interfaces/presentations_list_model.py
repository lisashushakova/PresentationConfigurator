from typing import List
from pydantic import BaseModel


class PresentationModel(BaseModel):
    id: str
    name: str
    owner_id: str
    modified_time: str


class PresentationsListModel(BaseModel):
    filtered_presentations: List['PresentationModel']
