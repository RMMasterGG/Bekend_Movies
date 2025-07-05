from fastapi import APIRouter, Path
from fastapi.params import Depends

from app.DatabaseLogic import database

from app.models import AddReview, PutReview
from app.security.TokenLogic import verify_token

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/{review_id}")
async def review_detail(review_id: int = Path(..., gt=0)):
    result = await database.get_review_in_reviews(review_id)
    return result

@router.post("/api/movies/{movie_id}")
async def add_movie_review(review: AddReview, movie_id: int = Path(..., gt=0), username: str = Depends(verify_token)):
    db_user = await database.get_user_data(username.get("sub"))
    print(username)
    result = await database.add_reviews(movie_id, review.text, review.rating, db_user.users_id)
    return result

@router.put("/{review_id}")
async def put_reviews(review: PutReview, review_id:int = Path(..., gt=0)):
    await database.put_review(review_id, review.text, review.rating)
    result = await database.get_review_in_reviews(review_id)
    result = result.copy()
    return result

@router.delete("/{reviews_id}")
async def delete_reviews(review_id: int = Path(..., gt=0)):
    result = await database.get_review_in_reviews(review_id)
    result = result.copy()
    await database.delete_review(review_id)
    return result
