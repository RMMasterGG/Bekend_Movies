from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Body, Request, Depends
from fastapi.params import Query

from app.DatabaseLogic import database
from app.models import SortOrder, SortField, AddMovie, PutMovie, MovieOther
from app.security.RoleLogic import PermissionChecker
from app.security.TokenLogic import verify_token

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/")
@PermissionChecker(["user"], rate_limit="30/minute")
async def get_movies(request: Request, current_user = Depends(verify_token), genre_id: Optional[int] = None,
    min_rating: Optional[float] = Query(None, ge=1, le=10),
    max_rating: Optional[float] = Query(None, ge=1, le=10),
    year: Optional[int] = None,
    sort_by: Optional[SortField] = None,
    sort_order: Optional[SortOrder] = SortOrder.ASC,
    limit: int = Query(10, le=100)):
    result = await database.get_movies(genre_id, min_rating, max_rating, year, sort_by, sort_order)
    if not result:
        raise HTTPException(status_code=404, detail="Movies not found")
    return result[0:int(limit)]

@router.get("/{movie_id}")
@PermissionChecker(["user"], rate_limit="30/minute")
async def get_movie_by_id(request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    result = await database.get_movies_id(movie_id)
    return result

@router.post("/movies")
@PermissionChecker(["admin"])
async def add_movie(movie: AddMovie, request: Request, current_user = Depends(verify_token)):
    await database.add_movies(title=movie.title, release_date=movie.release_date,
                              description=movie.description, duration=movie.duration, poster_url=movie.poster_url, rating=movie.rating)
    return movie

@router.put("/{movie_id}")
@PermissionChecker(["admin"])
async def update_movie(movie: PutMovie, request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    await database.put_movies(movie_id=movie_id, title=movie.title, release_date=movie.release_date,
                              description=movie.description, duration=movie.duration, poster_url=movie.poster_url, rating=movie.rating)
    result = await database.get_movies_id(movie_id)
    return result

@router.delete("/{movie_id}")
@PermissionChecker(["admin"])
async def delete_movie(request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    movie = await database.get_movies_id(movie_id)
    movie_details = movie.copy()
    await database.delete_movie(movie_id)
    return {"success": "Movie is deleted", "detail": movie_details}


@router.post("/{movie_id}/genres")
@PermissionChecker(["admin"])
async def add_movie_genres(genres_ids: MovieOther, request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    await database.add_genres_movie(movie_id, genres_ids.id)
    result = await database.get_movies_id(movie_id)
    return result

@router.delete("/{movie_id}/genres")
@PermissionChecker(["admin"])
async def delete_movie_genres(request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0), genres_ids: list[int] = Body(...)):
    await database.delete_genres_movie(movie_id, genres_ids)
    result = await database.get_movies_id(movie_id)
    return result

@router.post("/{movie_id}/actors")
@PermissionChecker(["admin"])
async def add_movie_actors(actors_ids: MovieOther, request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    await database.add_actors_movie(movie_id, actors_ids.id)
    result = await database.get_movies_id(movie_id)
    return result

@router.delete("/{movie_id}/actors")
@PermissionChecker(["admin"])
async def delete_movie_actors(request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0), actors_ids: list[int] = Body(...)):
    await database.delete_actors_movie(movie_id, actors_ids)
    result = await database.get_movies_id(movie_id)
    return result

@router.post("/{movie_id}/directors")
@PermissionChecker(["admin"])
async def add_movie_directors(directors_ids: MovieOther,request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    await database.add_directors_movie(movie_id, directors_ids.id)
    result = await database.get_movies_id(movie_id)
    return result

@router.delete("/{movie_id}/directors")
@PermissionChecker(["admin"])
async def delete_movie_directors(request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0), directors_ids: list[int] = Body(...)):
    await database.delete_directors_movie(movie_id, directors_ids)
    result = await database.get_movies_id(movie_id)
    return result

@router.get("/{movie_id}/reviews")
@PermissionChecker(["user"], rate_limit="30/minute")
async def movie_reviews(request: Request, current_user = Depends(verify_token), movie_id: int = Path(..., gt=0)):
    result = await database.get_reviews(movie_id)
    return result