from datetime import datetime
import logging
from logging import DEBUG

import colorlog
from colorlog.escape_codes import escape_codes
import sqlalchemy as db
from sqlalchemy import select, union, delete, extract, asc, desc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, joinedload

from app.LoggingLogic import create_logger
from app.models import SortOrder

# Формат строки подключения: dialect+driver://username:password@host:port/database
engine = create_async_engine("sqlite+aiosqlite:///.dbMovieSearch")
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

db_logger = create_logger(name="Database", get_logger="sqlalchemy.engine", level=DEBUG)

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    users_id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(512), index=True)
    refresh_token = db.Column(db.String(512), index=True)
    email = db.Column(db.String(255), db.CheckConstraint("email LIKE '%@%'"), unique=True, nullable=False)
    role = db.Column(db.String(20), db.CheckConstraint("role IN ('user', 'admin')"), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verify = db.Column(db.Boolean, default=False)

    reviews = relationship("Reviews", backref="user")

class Movies(Base):
    __tablename__ = "movies"
    movies_id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)
    poster_url = db.Column(db.String(512))
    rating = db.Column(db.Numeric(3, 1), db.CheckConstraint("rating >= 1 AND rating <= 10"), default=0.00)
    add_at = db.Column(db.DateTime, default=datetime.utcnow)
    put_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    genres = relationship("Genres", secondary="movie_genres", backref="movies")
    actors = relationship("People", secondary="movie_actors", backref="acted_in")
    directors = relationship("People", secondary="movie_directors", backref="directed_in")

class Genres(Base):
    __tablename__ = "genres"
    genres_id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100))

class People(Base):
    __tablename__ = "people"
    people_id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255))
    photo_url = db.Column(db.String(512))
    bio = db.Column(db.Text)
    role = db.Column(db.String(50))

class MovieGenres(Base):
    __tablename__ = "movie_genres"
    movies_id = db.Column(db.Integer, db.ForeignKey("movies.movies_id"), primary_key=True, index=True)
    genres_id = db.Column(db.Integer, db.ForeignKey("genres.genres_id"), primary_key=True, index=True)

class MovieActors(Base):
    __tablename__ = "movie_actors"
    movies_id = db.Column(db.Integer, db.ForeignKey("movies.movies_id"), primary_key=True, index=True)
    people_id = db.Column(db.Integer, db.ForeignKey("people.people_id"), primary_key=True, index=True)

class MovieDirectors(Base):
    __tablename__ = "movie_directors"
    movies_id = db.Column(db.Integer, db.ForeignKey("movies.movies_id"), primary_key=True, index=True)
    people_id = db.Column(db.Integer, db.ForeignKey("people.people_id"), primary_key=True, index=True)

class Reviews(Base):
    __tablename__ = "reviews"
    reviews_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    rating = db.Column(db.Integer, db.CheckConstraint("rating >= 1 AND rating <= 10"))
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    users_id = db.Column(db.Integer, db.ForeignKey("users.users_id"), index=True)
    movies_id = db.Column(db.Integer, db.ForeignKey("movies.movies_id"), index=True)

    movie = relationship("Movies", backref="reviews")

class DatabaseUtil:
    def __init__(self):
        self.engine = engine
        self.async_session = async_session

    async def create_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_user(self, username: str, password: str, access_token: str, refresh_token:str, email: str, role: str, expires_at: datetime):
        async with self.async_session() as session:
            exist = await session.execute(select(Users).where(Users.username == username or Users.email == email))
            if exist.scalars().first():
                raise ValueError("User with this email or username already exists")

            new_user = Users(username=username, password=password, access_token=access_token,
                             refresh_token=refresh_token, email=email, role=role, expires_at=expires_at)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user

    async def get_user(self, username: str, email: str) -> bool:
        async with self.async_session() as session:
            exist_is = False
            exist = await session.execute(select(Users).where(Users.username == username or Users.email == email))
            if exist.scalars().first():
                exist_is = True

            return exist_is

    async def get_user_data(self, username: str):
        async with self.async_session() as session:
            exist = await session.execute(select(Users).where(Users.username == username))
            user = exist.scalars().first()
            if not user:
                raise ValueError(f"User with name {username} not found")

            return user

    async def update_user(self, user_id: int, email: str | None = None, access_token: str | None = None, refresh_token: str | None = None,
                          expires_at: datetime | None = None, is_active: bool | None = None, is_verify: bool | None = None, explicit_null: bool = False):
        async with self.async_session() as session:
            user = await session.get(Users, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            update_values = {}
            if email is not None:
                update_values["email"] = email
            if access_token is not None or (explicit_null and access_token is None):
                update_values["access_token"] = access_token
            if refresh_token is not None or (explicit_null and access_token is None):
                update_values["refresh_token"] = refresh_token
            if expires_at is not None:
                update_values["expires_at"] = expires_at
            if is_active is not None:
                update_values["is_active"] = is_active
            if is_verify is not None:
                update_values["is_verify"] = is_verify

            await session.execute(db.update(Users).where(Users.users_id == user_id).values(**update_values))

            await session.refresh(user)
            await session.commit()

            return user

    async def update_user_password(self, user_id, new_password):
        async with self.async_session() as session:
            user = await session.get(Users, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            await session.execute(db.update(Users).where(Users.users_id == user_id and Users.password != new_password).values(password=new_password))
            await session.commit()
            await session.refresh(user)

            return user


    async def get_movies(self, genre_id = None, min_rating = None, max_rating = None, year = None, sort_by = None, sort_order = None):
        async with self.async_session() as session:
            stmt = select(Movies).options(joinedload(Movies.genres), joinedload(Movies.actors), joinedload(Movies.directors)).distinct()
            if genre_id:
                stmt = stmt.join(MovieGenres).where(MovieGenres.movies_id == genre_id)
            if min_rating is not None:
                stmt = stmt.where(Movies.rating >= min_rating)
            if max_rating is not None:
                stmt = stmt.where(Movies.rating <= max_rating)
            if year is not None:
                stmt = stmt.where(extract("year", Movies.release_date) == year)

            if sort_by:
                sort_field = getattr(Movies, sort_by.value)
                if sort_order == SortOrder.ASC:
                    stmt = stmt.order_by(asc(sort_field))
                else:
                    stmt = stmt.order_by(desc(sort_field))
            result = await session.execute(stmt)
            return result.unique().scalars().all()

    async def add_movies(self, title, release_date, description, duration, poster_url, rating):
        async with self.async_session() as session:
            new_movie = Movies(title=title, release_date=release_date, description=description, duration=duration, poster_url=poster_url, rating=rating)
            session.add(new_movie)
            await session.commit()
            return new_movie

    async def get_movies_id(self, movie_id):
        async with self.async_session() as session:
            result = await session.execute(select(Movies).where(Movies.movies_id == movie_id))
            return result.scalars().all()

    async def put_movies(self, movie_id, title = None, release_date = None, description = None, duration = None, poster_url = None, rating = None):
        async with self.async_session() as session:
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if release_date is not None:
                update_data["release_date"] = release_date
            if description is not None:
                update_data["description"] = description
            if duration is not None:
                update_data["duration"] = duration
            if poster_url is not None:
                update_data["poster_url"] = poster_url
            if rating is not None:
                update_data["rating"] = rating

            stmt = db.update(Movies).where(Movies.movies_id == movie_id).values(**update_data)
            await session.execute(stmt)
            await session.commit()

    async def delete_movie(self, movie_id):
        async with self.async_session() as session:
            stmt = delete(Movies).where(Movies.movies_id == movie_id)
            await session.execute(stmt)
            await session.commit()

    async def get_genres(self):
        async with self.async_session() as session:
            result = await session.execute(select(Genres))
            return result.scalars().all()

    async def add_genres(self, name):
        async with self.async_session() as session:
            new_genres = Genres(name=name)
            session.add(new_genres)
            await session.commit()
            return new_genres

    async def delete_genres(self, genres_id):
        async with self.async_session() as session:
            await session.execute(delete(Genres).where(Genres.genres_id == genres_id))
            await session.commit()

    async def get_genres_id(self, genres_id):
        async with self.async_session() as session:
            result = await session.execute(select(Genres).where(Genres.genres_id == genres_id))
            return result.scalars().all()

    async def get_people(self):
        async with self.async_session() as session:
            result = await session.execute(select(People))
            return result.scalars().all()

    async def get_people_id(self, people_id):
        async with self.async_session() as session:
            result = await session.execute(select(People).where(People.people_id == people_id))
            return result.scalars().all()

    async def add_people(self, name, photo_url, bio, role):
        async with self.async_session() as session:
            new_people = People(name=name, photo_url=photo_url, bio=bio, role=role)
            session.add(new_people)
            await session.commit()
            return new_people

    async def update_people(self, people_id, name = None, photo_url = None, bio = None, role = None):
        async with self.async_session() as session:
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if photo_url is not None:
                update_data["photo_url"] = photo_url
            if bio is not None:
                update_data["bio"] = bio
            if role is not None:
                update_data["role"] = role
            stmt = db.update(People).where(People.people_id == people_id).values(**update_data)
            await session.execute(stmt)
            await session.commit()

    async def delete_people(self, people_id):
        async with self.async_session() as session:
            stmt = delete(People).where(People.people_id == people_id)
            await session.execute(stmt)
            await session.commit()

    async def get_movie_people_id(self, people_id):
        async with self.async_session() as session:
            actor_stmt = select(Movies).join(MovieActors, Movies.movies_id == MovieActors.movies_id).where(MovieActors.people_id == people_id)

            director_stmt = select(Movies).join(MovieDirectors, Movies.movies_id == MovieDirectors.movies_id).where(MovieDirectors.people_id == people_id)

            stmt = union(actor_stmt, director_stmt)
            result = await session.execute(stmt)
            return result.unique().scalars().all()

    async def add_genres_movie(self, movie_id, genre_ids: list[int]):
        async with self.async_session() as session:
            existing_genre_ids = await session.execute(select(MovieGenres.genres_id).where(MovieGenres.movies_id == movie_id))
            existing_genre_ids = existing_genre_ids.scalars().all()
            for genre_id in genre_ids:
                if genre_id not in existing_genre_ids:
                    new_relation = MovieGenres(movies_id=movie_id, genres_id=genre_id)
                    session.add(new_relation)
            await session.commit()

    async def delete_genres_movie(self, movie_id, genre_ids: list[int]):
        async with self.async_session() as session:
            await session.execute(delete(MovieGenres).where(MovieGenres.movies_id == movie_id).where(MovieGenres.genres_id.in_(genre_ids)))
            await session.commit()

    async def add_actors_movie(self, movie_id, actors_ids: list[int]):
        async with self.async_session() as session:
            existing_result = await session.execute(select(MovieActors).where(MovieActors.movies_id == movie_id))
            existing_ids = set()
            for row in existing_result.all():
                existing_ids.add(row[0])

            for actors_id in actors_ids:
                if actors_id not in existing_ids:
                    new_relation = MovieActors(movies_id=movie_id, people_id=actors_id)
                    session.add(new_relation)
            await session.commit()

    async def delete_actors_movie(self, movie_id, actors_ids: list[int]):
        async with self.async_session() as session:
            await session.execute(delete(MovieGenres).where(MovieActors.movies_id == movie_id).where(MovieActors.people_id.in_(actors_ids)))
            await session.commit()

    async def add_directors_movie(self, movie_id, directors_ids: list[int]):
        async with self.async_session() as session:
            existing_result = await session.execute(select(MovieDirectors).where(MovieDirectors.movies_id == movie_id))
            existing_ids = set()
            for row in existing_result.all():
                existing_ids.add(row[0])

            for director_id in directors_ids:
                if director_id not in existing_ids:
                    new_relation = MovieDirectors(movies_id=movie_id, people_id=director_id)
                    session.add(new_relation)
            await session.commit()

    async def delete_directors_movie(self, movie_id, directors_ids: list[int]):
        async with self.async_session() as session:
            await session.execute(delete(MovieGenres).where(MovieDirectors.movies_id == movie_id).where(MovieDirectors.people_id.in_(directors_ids)))
            await session.commit()


    async def get_reviews(self, movie_id):
        async with self.async_session() as session:
            result = await session.execute(select(Reviews).where(Reviews.movies_id == movie_id))
            return result.scalars().all()

    async def add_reviews(self, movie_id, text, rating, user_id):
        async with self.async_session() as session:
            new_review = Reviews(text=text, rating=rating, users_id=user_id, movies_id=movie_id)

            session.add(new_review)
            await session.commit()
            return new_review

    async def get_review_in_reviews(self, review_id):
        async with self.async_session() as session:
            result = await session.execute(select(Reviews).where(Reviews.reviews_id == review_id))
            return result.scalars().all()

    async def put_review(self, review_id: int, text = None, rating = None):
        async with self.async_session() as session:
            update_data = {}
            if text is not None:
                update_data["text"] = text
            if rating is not None:
                update_data["rating"] = rating

            stmt = db.update(Reviews).where(Reviews.reviews_id == review_id).values(**update_data)
            await session.execute(stmt)
            await session.commit()

    async def delete_review(self, reviews_id):
        async with self.async_session() as session:
            stmt = delete(Reviews).where(Reviews.reviews_id == reviews_id)
            await session.execute(stmt)
            await session.commit()




database = DatabaseUtil()