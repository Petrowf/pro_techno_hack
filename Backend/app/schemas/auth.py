from pydantic import BaseModel
from typing import Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserAuth(BaseModel):
    login: str
    password: str

class UserCreate(BaseModel):
    login: str
    password: str
    username: str

class UserResponse(BaseModel):
    username: str
    login: str
    phone: Optional[str] = None  # Разрешаем None
    addresses: Optional[Dict[str, Any]] = None  # Для JSON-объекта
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    login: str
    password: str
