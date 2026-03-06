from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MediGraph API Running"}

app.include_router(items.router, prefix = "/api/v1", tags = ["items"])

