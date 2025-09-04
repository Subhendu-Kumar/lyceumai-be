from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from utils.db_util import lifespan_manager
from fastapi.middleware.cors import CORSMiddleware
from routes import (
    auth,
    classroom_admin,
    mermaid_gen_test,
    classroom_materials,
    classroom_enrollment,
    voice_assignment_test,
    classroom_announcement,
    classroom_comment,
    classroom_quiz,
)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with lifespan_manager():
        yield


# Create FastAPI instance with lifespan
app = FastAPI(
    version="1.0.0",
    lifespan=lifespan,
    title="Lyceum App API",
    description="A FastAPI application with Prisma & NeonDB",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include routers

# Auth routes
app.include_router(auth.router)

# Test routes
app.include_router(voice_assignment_test.router)
app.include_router(mermaid_gen_test.router)

# classroom routes
app.include_router(classroom_admin.router)
app.include_router(classroom_enrollment.router)
app.include_router(classroom_materials.router)
app.include_router(classroom_announcement.router)
app.include_router(classroom_comment.router)
app.include_router(classroom_quiz.router)


# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
async def root():
    return {
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
        "message": "FastAPI With Prisma & NeonDB",
    }


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    return {"status": "healthy", "message": "API is running successfully"}
