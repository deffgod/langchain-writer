from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="Neurofitness Training System API",
    description="API for generating and managing personalized neuro fitness training plans",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Neurofitness Training System API",
        "version": "1.0.0",
        "status": "active",
    }
