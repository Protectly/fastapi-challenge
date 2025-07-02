from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, hash_password
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = user_update.dict(exclude_unset=True)

    # Bug: No validation for unique email/username before update
    for field, value in update_data.items():
        if field == "password":
            # Hash the password before storing
            setattr(current_user, "hashed_password", hash_password(value))
        else:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


# Bug: Missing endpoint to deactivate user account
# Bug: Missing endpoint to get user statistics (task counts, etc.)
