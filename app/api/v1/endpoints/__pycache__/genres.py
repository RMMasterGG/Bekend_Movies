from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.params import Depends
from fastapi_cache.decorator import cache

from app.DatabaseLogic import database

from app.models import Genres
from app.security.RoleLogic import PermissionChecker
from app.security.limiter import limiter
from app.security.TokenLogic import verify_token

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/")
@cache(expire=60)
@PermissionChecker(["user"], rate_limit="1/minute")
async def genres_list(request: Request, current_user = Depends(verify_token)):
    result = await database.get_genres()
    if not result:
        raise HTTPException(status_code=404, detail="Genres not found")
    return result

@router.post("/")
@cache(expire=60)
@PermissionChecker(["admin"])
async def add_genres(request: Request, genres: Genres, current_user = Depends(verify_token)):
    new_genres = await database.add_genres(name=genres.name)
    return new_genres

@router.get("/{genres_id}")
@PermissionChecker(["user"], rate_limit="30/minute")
async def genres_list_id(request: Request, current_user = Depends(verify_token), genres_id: int = Path(..., gt=0)):
    result = await database.get_genres_id(genres_id=genres_id)
    if not result:
        raise HTTPException(status_code=404, detail="Genres not found")
    return result

@router.delete("/{genre_id}")
@PermissionChecker(["admin"])
async def delete_genre(request: Request, current_user = Depends(verify_token), genre_id: int = Path(..., gt=0)):
    genres = await database.get_genres_id(genres_id=genre_id)
    genres_details = genres.copy()
    await database.delete_genres(genres_id=genre_id)
    return {"success": "Genre is deleted", "details": genres_details}