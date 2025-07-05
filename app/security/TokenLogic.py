import logging

import jwt
import datetime
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict

from app.LoggingLogic import create_logger

security_logger = create_logger(name="Security", get_logger="__name__")

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_token(data: Dict, token_type: str):
    if token_type not in ('access', 'refresh'):
        security_logger.error(f"Полностью невалидный токен")
        raise ValueError("token_type должен быть 'access' или 'refresh'")
    to_encode = data.copy()
    if token_type == "access":
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        security_logger.warning(f"Просроченный токен: {token[:10]}...")
        raise HTTPException(401, "Токен истек")
    except jwt.InvalidTokenError as e:
        security_logger.error(f"Полностью невалидный токен: {str(e)}")
        raise HTTPException(401, "Неверные учетные данные")
