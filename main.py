# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.config import settings
from apis.base import api_router
from webapps.base import api_router as web_app_router
from db.session import engine
from db.base import Base

def include_router(app):
    app.include_router(api_router)
    app.include_router(web_app_router)


def configure_static(app:FastAPI):
    app.mount("/static",StaticFiles(directory="static"),name="static")

def create_tables():
    print("create tables")
    Base.metadata.create_all(bind=engine)

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    configure_static(app)
    create_tables()
    return app


app = start_application()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app",reload=True)
