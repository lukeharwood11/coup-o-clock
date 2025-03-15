from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import rooms, websockets
from pathlib import Path
import fastapi
import uvicorn


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        title="Coup O' Clock API",
        description="API for the Coup-o-Clock app",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routers
    app.include_router(rooms.router)
    app.include_router(websockets.router)

    # Mount static files
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def get_index():
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Welcome to Coup O' Clock API"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
