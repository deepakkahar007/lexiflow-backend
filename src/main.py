from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from config.settings import config
from db.client import close_database
from routes.Auth import authRouter
from routes.Document import documentRouter
from routes.Notebook import notebookRoute


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown resources."""

    yield

    await close_database()


app = FastAPI(
    title="Document Processing API",
    version="1.0.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CLIENT_URL,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

# Routes
app.include_router(authRouter)
app.include_router(documentRouter)
app.include_router(notebookRoute)


# Health check


class HealthCheckResponse(BaseModel):
    status: str


@app.get("/health", tags=["Health"], response_model=HealthCheckResponse)
def health_check():
    return HealthCheckResponse(status="OK")
