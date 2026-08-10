from fastapi import FastAPI

from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.assets import router as assets_router
from backend.api.routes.machines import router as machines_router


app = FastAPI(
    title="Platform360 IoT Assistant API",
    description="IoT monitoring and maintenance decision support backend.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Platform360 IoT Assistant API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


app.include_router(assets_router)
app.include_router(machines_router)
app.include_router(analysis_router)