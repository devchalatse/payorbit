"""Registration, login and current-user endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import (\n    ACCESS_TOKEN_MINUTES,\n    create_access_token,\n    hash_password,\n    verify_password,\n)
from app.db.session import get_db
from app.models.business import Business
from app.models.business_membership import BusinessMembership, MembershipRole
from app.models.user import User
from app.schemas.auth import (
    BusinessSummary,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _token_response(user: User, db: Session) -> TokenResponse:
    memberships = db.scalars(
        select(BusinessMembership).where(BusinessMembership.user_id == user.id)
    ).all()
    businesses = []
    for membership in memberships:
        business = db.get(Business, membership.business_id)
        if business is not None:
            businesses.append(
                BusinessSummary(id=business.id, name=business.name, role=str(membership.role))
            )
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=ACCESS_TOKEN_MINUTES * 60,
        user=UserRead(id=user.id, full_name=user.full_name, email=user.email),
        businesses=businesses,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = User(
        full_name=payload.full_name,
        email=str(payload.email).lower(),
        password_hash=hash_password(payload.password),
    )
    business = Business(
        name=payload.business_name,
        registration_number=payload.business_registration_number,
        email=str(payload.business_email).lower(),
    )
    db.add_all([user, business])
    db.flush()
    db.add(
        BusinessMembership(
            user_id=user.id,
            business_id=business.id,
            role=MembershipRole.OWNER,
        )
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account or business with those unique details already exists.",
        ) from exc
    db.refresh(user)
    return _token_response(user, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if (\n        user is None\n        or not user.is_active\n        or not verify_password(payload.password, user.password_hash)\n    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_response(user, db)


@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)) -> User:
    return user
