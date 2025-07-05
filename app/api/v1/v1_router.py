from fastapi import APIRouter, Depends
from .endpoints import auth, genres, movies, people, reviews
from ...security.TokenLogic import verify_token

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth.router)
v1_router.include_router(genres.router, dependencies=[Depends(verify_token)])
v1_router.include_router(movies.router, dependencies=[Depends(verify_token)])
v1_router.include_router(people.router, dependencies=[Depends(verify_token)])
v1_router.include_router(reviews.router, dependencies=[Depends(verify_token)])