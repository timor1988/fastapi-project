# -*- coding: utf-8 -*-
from typing import Union

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, Response
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import status, HTTPException

from db.models.users import User
from db.session import get_db
from core.hashing import Hasher
from schemas.tokens import Token
from db.respository.login import get_user
from core.security import create_access_token
from core.config import settings
from apis.utils import OAuth2PasswordBearerWithCookie

router = APIRouter()

oauth2_schema = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


def authenticate_user(username: str, password: str, db: Session) -> Union[bool, User]:
    user = get_user(username=username, db=db)
    print(user)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False

    return user


def get_current_user_from_token(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        #print("username/email extracted is ", username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    # 1. 验证用户信息
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    # 2.验证通过之后生成token
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user.email}
    access_token = create_access_token(data=data, expire_delta=expire)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}
