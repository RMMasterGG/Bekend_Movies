import secrets
import uuid

from passlib.hash import bcrypt
from redis import Redis

redis = Redis(host="localhost", port=6379, db=1)


def hash_password(password: str):
    password_hash = bcrypt.hash(password)
    return password_hash

def verify_password(password_hash: str, password: str) -> bool:
    password_is = bcrypt.verify(hash=password_hash, secret=password)
    return password_is

def correct_username(username: str, input_username: str):
    username_is = secrets.compare_digest(username, input_username)
    return username_is

def create_verify_code(email: str):
    session_id  = str(uuid.uuid4())
    code = str(secrets.randbelow(900000) + 100000)
    data = dict(email=email, code=code, attempts=0)
    redis.setex(name=f"verify:{session_id}", time=600, value=str(data))
    return session_id, code

def verify_code(session_id: str, user_code: str):
    data = redis.get(f"verify:{session_id}")
    if not data:
        return False
    remaining_ttl = redis.ttl(f"verify:{session_id}")
    if remaining_ttl < 0:
        return False
    data = eval(data.decode())
    data["attempts"] += 1
    if data["attempts"] > 5:
        redis.delete(f"verify:{session_id}")
        return False
    if data["code"] == user_code:
        redis.delete(f"verify:{session_id}")
        return True
    else:
        redis.setex(f"verify:{session_id}", remaining_ttl, str(data))
        return False
