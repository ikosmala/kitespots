from fastapi import FastAPI
from .routers import users
from fastapi.middleware.cors import CORSMiddleware
from .models import Base
from .database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)


@app.get("/")
async def info():
    return {"info": "App is working"}
