from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    StringConstraints,
    Field,
    SecretStr,
)
from datetime import datetime
from typing import Annotated, Optional

MIN_PASSWORD_LENGTH = 5
MIN_NAME_LENGTH = 2


class UserBase(BaseModel):
    email: EmailStr
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=MIN_NAME_LENGTH)
    ]


class UserCreate(UserBase):
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
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
    email: EmailStr | None = None
