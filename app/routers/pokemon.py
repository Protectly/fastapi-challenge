from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
import httpx

from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.task import Pokemon, PokemonSearchResponse

router = APIRouter()

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


@router.get("/", response_model=PokemonSearchResponse)
async def get_pokemon_list(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get a list of Pokemon with pagination"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{POKEAPI_BASE_URL}/pokemon", params={"limit": limit, "offset": offset}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch Pokemon data")

        data = response.json()

        pokemon_list = []
        for pokemon_data in data["results"]:
            pokemon_detail = await get_pokemon_detail(pokemon_data["url"])
            if pokemon_detail:
                pokemon_list.append(pokemon_detail)

        return PokemonSearchResponse(
            results=pokemon_list,
            count=data["count"],
            next_url=data.get("next"),
            previous_url=data.get("previous"),
        )


@router.get("/{pokemon_id}", response_model=Pokemon)
async def get_pokemon(
    pokemon_id: int,
    current_user: User = Depends(get_current_user),
):
    """Get detailed information about a specific Pokemon"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_id}")

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        elif response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch Pokemon data")

        pokemon_data = response.json()

        return Pokemon(
            id=pokemon_data["id"],
            name=pokemon_data["name"],
            height=pokemon_data["height"],
            weight=pokemon_data["weight"],
            types=[t["type"]["name"] for t in pokemon_data["types"]],
            abilities=[a["ability"]["name"] for a in pokemon_data["abilities"]],
            sprite_url=pokemon_data["sprites"]["front_default"],
        )


@router.post("/search/{name}", response_model=Pokemon)
async def search_pokemon_by_name(
    name: str,
    current_user: User = Depends(get_current_user),
):
    """Search for a Pokemon by name"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}")

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Pokemon '{name}' not found")
        elif response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch Pokemon data")

        pokemon_data = response.json()

        return Pokemon(
            id=pokemon_data["id"],
            name=pokemon_data["name"],
            height=pokemon_data["height"],
            weight=pokemon_data["weight"],
            types=[t["type"]["name"] for t in pokemon_data["types"]],
            abilities=[a["ability"]["name"] for a in pokemon_data["abilities"]],
            sprite_url=pokemon_data["sprites"]["front_default"],
        )


async def get_pokemon_detail(pokemon_url: str) -> Optional[Pokemon]:
    """Helper function to get detailed Pokemon information"""
    async with httpx.AsyncClient() as client:
        response = await client.get(pokemon_url)

        if response.status_code != 200:
            return None

        pokemon_data = response.json()

        return Pokemon(
            id=pokemon_data["id"],
            name=pokemon_data["name"],
            height=pokemon_data["height"],
            weight=pokemon_data["weight"],
            types=[t["type"]["name"] for t in pokemon_data["types"]],
            abilities=[a["ability"]["name"] for a in pokemon_data["abilities"]],
            sprite_url=pokemon_data["sprites"]["front_default"],
        )
