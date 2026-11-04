"""Business request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BusinessCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    registration_number: str | None = Field(default=None, max_length=80)
    email: EmailStr


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    registration_number: str | None
    email: str
    created_at: datetime
