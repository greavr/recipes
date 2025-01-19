from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


# Import DB
from .database import engine, get_db

# Import Routes
from v1 import api
from admin import admin_api


# Boot Strap
import models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(admin_api.router)

def Configure_Logging():
    """ Function to build logging"""
    import logging
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler, setup_loggin
    logging.basicConfig(level=logging.INFO)
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    logging.getLogger().setLevel(logging.DEBUG)
    setup_logging(handler)


if __name__ == "__main__":
    # Enable Logging
    Configure_Logging()


    # Run Web App
    uvicorn.run(app, host="0.0.0.0", port=8080)