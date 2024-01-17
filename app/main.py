# app/main.py
from fastapi import FastAPI
from . import models
from .db import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
