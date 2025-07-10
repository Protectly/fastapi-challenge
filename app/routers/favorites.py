from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Favorite
from app.schemas.task import (
    FavoriteCreate,
    Favorite as FavoriteSchema,
    FavoriteResponse,
)

router = APIRouter()


@router.get("/", response_model=FavoriteResponse)
def get_user_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's favorite Pokemon"""
    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.is_active == True)
        .all()
    )

    return FavoriteResponse(favorites=favorites, total=len(favorites))


@router.post(
    "/{pokemon_id}", response_model=FavoriteSchema, status_code=status.HTTP_201_CREATED
)
def add_pokemon_to_favorites(
    pokemon_id: int,
    pokemon_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a Pokemon to user's favorites"""
    # Check if already in favorites
    existing_favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.pokemon_id == pokemon_id)
        .first()
    )

    if existing_favorite:
        if existing_favorite.is_active:
            raise HTTPException(
                status_code=400, detail="Pokemon is already in favorites"
            )
        else:
            # Reactivate the favorite
            existing_favorite.is_active = True
            db.commit()
            db.refresh(existing_favorite)
            return existing_favorite

    # Create new favorite
    favorite = Favorite(
        user_id=current_user.id, pokemon_id=pokemon_id, pokemon_name=pokemon_name
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{pokemon_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pokemon_from_favorites(
    pokemon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a Pokemon from user's favorites"""
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.pokemon_id == pokemon_id,
            Favorite.is_active == True,
        )
        .first()
    )

    if not favorite:
        raise HTTPException(status_code=404, detail="Pokemon not found in favorites")

    # Soft delete by setting is_active to False
    favorite.is_active = False
    db.commit()


@router.get("/check/{pokemon_id}")
def check_pokemon_in_favorites(
    pokemon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if a Pokemon is in user's favorites"""
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.pokemon_id == pokemon_id,
            Favorite.is_active == True,
        )
        .first()
    )

    return {"is_favorite": favorite is not None}
