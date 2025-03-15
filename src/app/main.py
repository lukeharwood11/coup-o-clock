import fastapi
import boto3
import uvicorn
from botocore.exceptions import ClientError
from app.routers import rooms


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

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
