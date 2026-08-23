from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import config

origins = ["http://localhost:5173"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World", "res": config.PASSWORD_HASH_SECRET}
