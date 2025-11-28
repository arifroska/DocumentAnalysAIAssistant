from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from passlib.context import CryptContext
import os

auth = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

allowed_username = os.getenv("AUTH_USERNAME")
plain_password = os.getenv("AUTH_PASSWORD")

if plain_password:
    hashed_password = pwd_context.hash(plain_password)

user = {
    allowed_username : hashed_password
}

def verify_password(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass, hashed_pass)

def get_auth(credentials: Annotated[HTTPBasicCredentials, Depends(auth)]):
    username = credentials.username
    password = credentials.password

    print("username :", username, " || password :",password)

    if username not in user or not verify_password(password, user[allowed_username]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kredential tidak valid",
            headers={"WWW-Authenticate": "Basic"}
        )
    return username

Authuser = Annotated[str, Depends(get_auth)]