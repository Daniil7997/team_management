from fastapi import FastAPI

from app.bootstrap.application import configure_application
from app.bootstrap.lifespan import lifespan

application = FastAPI(lifespan=lifespan)

configure_application(application)
