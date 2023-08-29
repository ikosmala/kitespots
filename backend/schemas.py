from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    StringConstraints,
    Field,
    SecretStr,
)
from datetime import datetime
from typing import Annotated

MIN_PASSWORD_LENGTH = 5


class UserCreate(BaseModel):
    email: EmailStr
    name: Annotated[str, StringConstraints(strip_whitespace=True)]
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: Annotated[str, StringConstraints(strip_whitespace=True)]
    created_at: datetime
    active: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=MIN_PASSWORD_LENGTH)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
