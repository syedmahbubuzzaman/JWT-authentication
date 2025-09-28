import os
from dotenv import load_dotenv
from db import Base
from sqlalchemy import  Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta

load_dotenv

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    tokens = relationship("RefreshToken", back_populates="user")    

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="tokens")

    @staticmethod
    def create(user_id: int):
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        return {"token": token, "user_id": user_id, "expires_at": expires_at}
    