from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.assets import router as assets_router
from backend.api.routes.machines import router as machines_router
from backend.api.routes.assistant import (
    router as assistant_router,
)


app = FastAPI(
    title="IoT Maintenance Assistant API",
    description=(
        "Industrial IoT monitoring and "
        "maintenance decision support backend."
    ),
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["System"])
def root():
    return {
        "message": "IoT Maintenance Assistant API"
    }


@app.get("/health",tags=["System"])
def health_check():
    return {
        "status": "ok"
    }


app.include_router(assets_router)
app.include_router(machines_router)
app.include_router(analysis_router)
app.include_router(assistant_router)