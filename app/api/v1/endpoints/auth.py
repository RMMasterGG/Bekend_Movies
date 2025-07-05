import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request, Query

from app.security.TokenLogic import verify_token, create_token
from app.security.other import hash_password, verify_password, create_verify_code, verify_code
from app.SendEmailLogic import send_email
from app.tasks.email import send_verification_email
from fastapi import BackgroundTasks

from app.DatabaseLogic import database

from app.models import RegisterUser, LoginUser

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register_user(user: RegisterUser, response: Response, background_tasks: BackgroundTasks):
    user_is = await database.get_user(username=user.username, email=user.email)
    if user_is:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    hashed_password  = hash_password(user.password)
    access_token = create_token(data=dict(sub=user.username), token_type="access")
    refresh_token = create_token(data=dict(sub=user.username), token_type="refresh")
    expires_at = datetime.utcnow() + timedelta(days=30)
    await database.create_user(username=user.username, password=hashed_password, access_token=access_token,
                               refresh_token=refresh_token, email=user.email, role=user.role, expires_at=expires_at)

    # ГЕНЕРАЦИЯ ТОКЕНА ДЛЯ MAIL

    session_id, code = create_verify_code(email=str(user.email))

    background_tasks.add_task(send_verification_email.delay, json.dumps(dict(email=user.email, code=code, session_id=session_id, username=user.username)))


    response.set_cookie(
        key="verification_session",
        value=session_id,
        max_age=600,
        httponly=True,
        samesite='lax'
    )

    return dict(status="Регистрация прошла успешно!")

@router.get("/verify-email")
async def verify_email_user(request: Request, session_id: Optional[str] = Query(None),
                            code: str = Query(...), username: str = Query(...)):

    db_user = await database.get_user_data(username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")
    if db_user.is_verify:
        raise HTTPException(309, "Данный пользователь уже верифицирован!")

    session_id = request.cookies.get("verification_session") or session_id
    if not session_id:
        raise HTTPException(status_code=309, detail="Ошибка!")
    if not verify_code(session_id=session_id, user_code=code):
        raise HTTPException(status_code=309, detail="Ошибка!")
    else:
        await database.update_user(db_user.users_id, is_verify=True)
        access_token = create_token(data=dict(sub=db_user.username), token_type="access")
        return dict(accss_token=access_token)


@router.post("/login")
async def login_user(user: LoginUser = Depends(LoginUser.as_form), response: Response = None):
    db_user = await database.get_user_data(user.username)
    if not db_user:
        raise HTTPException(401, detail="Invalid user or password")
    if not verify_password(db_user.password, user.password):
        raise HTTPException(401, detail="Invalid user or password")
    access_token = create_token(data=dict(sub=db_user.username), token_type="access")

    if not db_user.access_token or not db_user.expires_at or datetime.utcnow() >= db_user.expires_at:
        refresh_token = create_token(data=dict(sub=db_user.username), token_type="refresh")
        expires_at = datetime.utcnow() + timedelta(days=30)
    else:
        refresh_token = db_user.refresh_token
        expires_at = db_user.expires_at

    await database.update_user(user_id=db_user.users_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at, is_active=True)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        max_age=43200 * 60
    )

    return dict(access_token=access_token)



@router.post("/logout", dependencies=[Depends(verify_token)])
async def logout_user(response: Response = None, username: str = Depends(verify_token)):
    db_user = await database.get_user_data(username.get("sub"))
    user = await database.update_user(user_id=db_user.users_id, access_token=None, refresh_token=None, is_active=False, explicit_null=True)

    response.delete_cookie("refresh_token")

    return user

@router.post("/refresh", dependencies=[Depends(verify_token)])
async def user_me(request: Request, refresh_token: str = Body(..., embed=True)):
    token = request.cookies.get("refresh_token") or refresh_token
    if not token:
        raise HTTPException(401, "Refresh token required")

    payload = verify_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token required")
    username = payload.get("sub")
    db_user = await database.get_user_data(username)
    if db_user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_token(data=dict(sub=db_user.username), token_type="access")

    return dict(access_token=access_token)
