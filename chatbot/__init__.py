from dotenv import load_dotenv

load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from chatbot.engine import get_knowledge_engine
from chatbot.settings import settings
from chatbot.routers import (
    chat,
    video
)

environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set

app = FastAPI()
knowledge_engine = get_knowledge_engine()

app.include_router(chat.router)
app.include_router(video.router)

if environment == "dev":
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if settings.create_knowledge_base:
    logger.debug("Creating knowledge base from documents.")
    knowledge_engine.create_knowledge_base()
else:
    logger.debug("Knowledge already created. Load index from storage.")
    knowledge_engine.load_index_from_storage()
    logger.debug("Index loaded from storage.")

knowledge_engine.create_chat_engine()

@app.get("/")
async def root():
    return {
        "message": "Hello, World!",
    }