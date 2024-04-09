import datetime as dt
import pydantic as pydantic
from typing import Optional


class _UserBase(pydantic.BaseModel):
    email: str


class UserCreate(_UserBase):
    hashed_password: str

    class Config:
        from_attributes = True


class User(_UserBase):
    id: int

    class Config:
        from_attributes = True


class _LeadBase(pydantic.BaseModel):
    grafica_url: str
    grafica_type: str


class LeadCreate(_LeadBase):
    pass


class Lead(_LeadBase):
    id: int
    owner_id: int
    date_created: dt.datetime
    date_last_updated: Optional[dt.datetime] = None

    class Config:
        from_attributes = True
