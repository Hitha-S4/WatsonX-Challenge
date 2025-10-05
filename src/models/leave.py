from typing import List
from pydantic import BaseModel
from datetime import date


class Leave(BaseModel):
    ocassion: str
    date: date

