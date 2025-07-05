from typing import Optional

from fastapi import HTTPException, Request
from functools import wraps
from app.security.limiter import limiter

from app.DatabaseLogic import database


class PermissionChecker:
    def __init__(self, roles: list[str], rate_limit: Optional[str] = None):
        self.roles = roles
        self.rate_limit = rate_limit

    def __call__(self, func):
        if self.rate_limit:
            limited_func = limiter.limit(self.rate_limit)(func)
        else:
            limited_func = func

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")

            db_user = await database.get_user_data(current_user.get("sub"))
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            if db_user.role == "admin":
                return await func(request, *args, **kwargs)

            if db_user.role not in self.roles and db_user.role != "admin":
                raise HTTPException(status_code=403, detail="Permission denied")

            return await limited_func(request, *args, **kwargs)

        return wrapper


