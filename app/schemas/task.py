from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class PokemonBase(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    types: List[str]


class Pokemon(PokemonBase):
    abilities: List[str]
    sprite_url: Optional[str] = None

    class Config:
        from_attributes = True


class PokemonSearchResponse(BaseModel):
    results: List[Pokemon]
    count: int
    next_url: Optional[str] = None
    previous_url: Optional[str] = None


class FavoriteBase(BaseModel):
    pokemon_id: int
    pokemon_name: str


class FavoriteCreate(FavoriteBase):
    pass


class Favorite(FavoriteBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteResponse(BaseModel):
    favorites: List[Favorite]
    total: int
