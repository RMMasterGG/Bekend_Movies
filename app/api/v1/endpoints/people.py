from fastapi import APIRouter, Path
from app.DatabaseLogic import database
from app.models import AddPeople

router = APIRouter(prefix="/people", tags=["People"])


@router.get("/")
async def peoples():
    result = await database.get_people()
    return result

@router.get("/{people_id}")
async def info_people_id(people_id: int = Path(..., gt=0)):
    result = await database.get_people_id(people_id=people_id)
    return result

@router.post("/")
async def create_people(people: AddPeople):
    result = await database.add_people(people.name, people.photo_url, people.bio, people.role)
    return result

@router.put("/{people_id}")
async def update_people(people: AddPeople, people_id: int = Path(..., gt=0)):
    await database.update_people(people_id, people.name, people.photo_url, people.bio, people.role)
    result = await database.get_movies_id(people_id)
    return result

@router.delete("/{people_id}")
async def delete_people(people_id: int = Path(..., gt=0)):
    people = await database.get_people_id(people_id=people_id)
    result = people.copy()
    await database.delete_people(people_id=people_id)
    return {"success": "People is deleted", "details": result}

@router.get("/{people_id}/movies")
async def movies_people_id(people_id: int = Path(..., gt=0)):
    result = await database.get_movie_people_id(people_id=people_id)
    return result