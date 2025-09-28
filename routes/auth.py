from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from models import User, RefreshToken
from authutils import hash_password, verify_password, create_access_token, decode_access_token
from datetime import datetime

router = APIRouter()

# Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    refresh_token: str


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    return {"msg": "User created successfully"}


@router.post("/login", response_model=TokenPair)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(sub=db_user.username)

    token_data = RefreshToken.create(user_id=db_user.id)
    db_token = RefreshToken(**token_data)
    db.add(db_token)
    db.commit()

    return {"access_token": access_token, "token_type": "Bearer", "refresh_token": db_token.token}


@router.post("/refresh", response_model=TokenPair)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db_token.user
    db_token.revoked = True

    new_data = RefreshToken.create(user_id=user.id)
    new_db_token = RefreshToken(**new_data)
    db.add(new_db_token)
    db.commit()

    new_access = create_access_token(sub=user.username)

    return {"access_token": new_access, "token_type": "Bearer", "refresh_token": new_db_token.token}


@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if db_token:
        db_token.revoked = True
        db.commit()
    return {"msg": "Logged out"}


@router.get("/me")
def me(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    payload = decode_access_token(token)
    return {"username": payload["sub"], "issued_at": payload["iat"], "expires": payload["exp"]}
