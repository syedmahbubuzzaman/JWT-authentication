from fastapi import FastAPI
from routes import auth

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"msg": "JWT Authentication API running"}
