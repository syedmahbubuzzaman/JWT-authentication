from fastapi import FastAPI
from routes import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# ✅ Allow frontend origin
origins = [
    "http://localhost:3000",   # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # origins allowed
    allow_credentials=True,         # needed for cookies (refresh token)
    allow_methods=["*"],            # allow all methods (POST, GET, etc.)
    allow_headers=["*"],            # allow all headers (Authorization, etc.)
)


app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"msg": "JWT Authentication API running"}
#my new line