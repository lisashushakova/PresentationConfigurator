from pydantic import BaseModel


class UserInfoModel(BaseModel):
    username: str
    iconURL: str
