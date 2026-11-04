"""Authentication request and response schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    business_registration_number: str | None = Field(default=None, max_length=80)
    business_email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr


class BusinessSummary(BaseModel):
    id: UUID
    name: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
    businesses: list[BusinessSummary]
