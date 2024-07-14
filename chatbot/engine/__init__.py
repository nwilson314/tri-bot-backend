from typing import Generator

from .knowledge_engine import KnowledgeEngine

from chatbot.settings import settings


knowledge_engine = KnowledgeEngine(settings.data_path)

def get_knowledge_engine_dep() -> Generator[KnowledgeEngine, None, None]:
    yield knowledge_engine


def get_knowledge_engine() -> KnowledgeEngine:
    return knowledge_engine