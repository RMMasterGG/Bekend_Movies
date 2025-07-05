from enum import Enum
from typing import Annotated, Optional, Literal

from fastapi import Form
from datetime import date
from pydantic import BaseModel, Field, field_validator,conlist, EmailStr
from typing import Annotated


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    TITLE = "title"
    RELEASE_DATE = "release_date"
    RATING = "rating"

class RegisterUser(BaseModel):
    username: str = Field(..., min_length=1, max_length=100,)
    password: str = Field(min_length=6, max_length=255)
    email: EmailStr
    role: Literal["user", "admin"] = Field(default="user")

class LoginUser(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(cls, username: str = Form(), password: str = Form()):
        username = username
        return cls(username=username, password=password)

class AddMovie(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: date
    description: str = Field(..., min_length=1)
    duration: int = Field(..., ge=1)
    poster_url: str = Field(..., pattern=r"^https?://", max_length=512)
    rating: float = Field(..., ge=1.0, le=10.0)

    @field_validator('release_date')
    def validate_date(cls, v: date) -> date:
        if v.year < 1888:
            raise ValueError("Release year cannot be before 1888")
        if v > date.today():
            raise ValueError("Release date cannot be in the future")
        return v

class PutMovie(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    release_date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1)
    duration: Optional[int] = Field(None, ge=1)
    poster_url: Optional[str] = Field(None, pattern=r"^https?://", max_length=512)
    rating: Optional[float] = Field(None, ge=1.0, le=10.0)

    @field_validator('release_date')
    def validate_date(cls, v: date) -> date:
        if v.year < 1888:
            raise ValueError("Release year cannot be before 1888")
        if v > date.today():
            raise ValueError("Release date cannot be in the future")
        return v

class Genres(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class AddPeople(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    photo_url: str = Field(..., pattern=r"^https?://", max_length=512)
    bio: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1, max_length=50)

class PutPeople(BaseModel):
    name: str = Field(None, min_length=1, max_length=255)
    photo_url: str = Field(None, pattern=r"^https?://", max_length=512)
    bio: str = Field(None, min_length=1)
    role: str = Field(None, min_length=1, max_length=50)

class MovieOther(BaseModel):
    id: conlist(int, min_length=1) = Field(..., examples=[[1, 2, 3]])

    @field_validator('id')
    def validate_date(cls, v: list[int]) -> list[int]:
        for _ in v:
            if  _ < 1:
                raise ValueError("Все ID жанров должны быть ≥ 1")
        return v

class AddReview(BaseModel):
    text: str = Field(..., min_length=1)
    rating: float = Field(..., ge=1.0, le=10.0)

class PutReview(BaseModel):
    text: str = Field(None, min_length=1)
    rating: float = Field(None, ge=1.0, le=10.0)