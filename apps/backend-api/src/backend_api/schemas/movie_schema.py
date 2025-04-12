from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_date: Optional[date] = None
    genre_ids: List[int] = []


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    id: int
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None

    class Config:
        orm_mode = True
