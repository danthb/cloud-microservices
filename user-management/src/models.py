import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    username: str
    email: str
    password: str
    salt: str
    token: str
    created_at: datetime.datetime
    expire_at: datetime.datetime


class UserRequest(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    created_at: str


class UserAuth(BaseModel):
    username: str
    password: str


class UserAuthResponse(BaseModel):
    id : int
    token: str
    expire_at: str


class UserInfo(BaseModel):
    id: int
    username: str
    email : str