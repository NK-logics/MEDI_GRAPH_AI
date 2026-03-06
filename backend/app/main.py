from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MediGraph API Running"}

@app.get("/")