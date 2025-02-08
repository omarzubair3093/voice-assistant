from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from assistant.assistant_controller import controller as AssistantAudioController
from project_config import setup_app_config


def create_app() -> FastAPI:
    setup_app_config()
    app = FastAPI()

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Setup templates
    templates = Jinja2Templates(directory="templates")

    origins = [
        "http://localhost",
        "http://localhost:3000",
        "*"
    ]

    app.include_router(AssistantAudioController, tags=['assistant'])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    return app


app = create_app()