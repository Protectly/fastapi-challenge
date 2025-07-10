from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, hash_password
from app.models.user import User
from app.schemas.user import UserUpdate, User as UserSchema

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "password":
            hashed_password = hash_password(value)
            setattr(current_user, "hashed_password", hashed_password)
        elif field == "email":
            # Check if email is already taken
            existing_user = (
                db.query(User)
                .filter(User.email == value, User.id != current_user.id)
                .first()
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            setattr(current_user, field, value)
        elif field == "username":
            # Check if username is already taken
            existing_user = (
                db.query(User)
                .filter(User.username == value, User.id != current_user.id)
                .first()
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deactivate current user account"""
    current_user.is_active = False
    db.commit()
