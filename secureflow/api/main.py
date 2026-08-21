from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from secureflow.db.database import init_db, engine
from secureflow.api.routes.payments import router as payments_router
from secureflow.api.routes.events import router as events_router
from secureflow.api.routes.entities import router as entities_router
from secureflow.api.routes.scenarios import router as scenarios_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema is initialized on API startup."""
    init_db(engine)
    yield

app = FastAPI(
    title="SecureFlow REST API",
    description="Adaptive AI Security Layer for Digital Payments (Razorpay AI Risk Manager Prototype)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware Setup for Frontend Simulation UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router Modules
app.include_router(payments_router)
app.include_router(events_router)
app.include_router(entities_router)
app.include_router(scenarios_router)

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SecureFlow Security Engine API", "version": "1.0.0"}
