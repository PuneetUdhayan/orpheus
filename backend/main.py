from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class GreetRequest(BaseModel):
    name: str

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/greet")
def greet_user(data: GreetRequest):
    return {"greeting": f"Hello, {data.name}!"}