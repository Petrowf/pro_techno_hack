from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    login: str
    password: str
    name: str


class LoginRequest(BaseModel):
    login: str
    password: str
