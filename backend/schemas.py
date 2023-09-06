from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    StringConstraints,
    Field,
)
from pydantic_extra_types.coordinate import Longitude, Latitude
from pydantic_extra_types.country import CountryShortName

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
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
    email: EmailStr | None = None


class SpotIn(BaseModel):
    latitude: Latitude  # first - szerokosc
    longitude: Longitude  # second - dlugosc
    name: str = Field(..., min_length=2)
    country: CountryShortName

    # todo: validate latitude and longitude to 14 places after decimal


class Spot(SpotIn):
    id: int


class SpotOut(Spot):
    model_config = ConfigDict(from_attributes=True)
    pass


class SpotUpdate(BaseModel):
    latitude: Optional[Latitude] = None  # first - szerokosc
    longitude: Optional[Longitude] = None  # second - dlugosc
    name: Optional[str] = Field(None, min_length=2)
    country: Optional[CountryShortName] = None


class UserWithSpots(UserOut):
    spots: Optional[list[SpotOut]]
