from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config.settings import config
from db.client import close_database
from routes.Auth import authRouter
from routes.Document import documentRouter


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


# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "OK"}
