from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.routers import auth, tasks, users


# Bug: Missing proper lifespan context manager setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown - nothing to clean up


app = FastAPI(
    title=settings.project_name,
    # Bug: Missing version, description, and other metadata
    debug=settings.debug,
    lifespan=lifespan,
)

# Bug: CORS middleware too permissive
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(tasks.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)


@app.get("/")
def read_root():
    return {"message": "Welcome to Task Management API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Bug: Missing proper error handlers
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    # Bug: Exposing internal error details
    return HTTPException(status_code=500, detail=str(exc))
