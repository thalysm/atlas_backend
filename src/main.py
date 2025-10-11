from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .core.database import connect_to_mongo, close_mongo_connection
from .presentation.routes import (
    auth_routes,
    exercise_routes,
    workout_package_routes,
    workout_session_routes,
    analytics_routes,
    competition_group_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
    close_mongo_connection()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan, root_path=settings.ROOT_PATH)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(exercise_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(workout_package_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(workout_session_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(competition_group_routes.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {"message": "Atlas API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
