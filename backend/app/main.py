from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, health

app = FastAPI(title="MediGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "MediGraph API Running"}


app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, tags=["auth"])

