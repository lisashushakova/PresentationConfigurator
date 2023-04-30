from typing import List, Union

from pydantic import BaseModel


class PresentationModel(BaseModel):
    id: str
    name: str
    type: str
    modifiedTime: str
    parents: List[str]


class FolderModel(BaseModel):
    id: str
    name: str
    type: str
    mark: bool
    children: List[Union['FolderModel', 'PresentationModel']]
