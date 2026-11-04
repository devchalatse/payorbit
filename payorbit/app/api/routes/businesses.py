"""Business endpoints scoped to the authenticated user's memberships."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.business import Business
from app.models.business_membership import BusinessMembership, MembershipRole
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessRead

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
def create_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Business:
    business = Business(**payload.model_dump())
    db.add(business)
    try:
        db.flush()
        db.add(
            BusinessMembership(
                business_id=business.id, user_id=user.id, role=MembershipRole.OWNER
            )
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="A business with that registration number already exists."
        ) from exc
    db.refresh(business)
    return business


@router.get("", response_model=list[BusinessRead])
def list_businesses(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Business]:
    statement = (
        select(Business)
        .join(BusinessMembership)
        .where(BusinessMembership.user_id == user.id)
        .order_by(Business.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.get("/{business_id}", response_model=BusinessRead)
def get_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Business:
    business = db.scalar(
        select(Business)
        .join(BusinessMembership)
        .where(Business.id == business_id, BusinessMembership.user_id == user.id)
    )
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found.")
    return business
