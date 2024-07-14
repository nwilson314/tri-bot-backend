from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from loguru import logger

from chatbot.settings import settings


Settings.llm = OpenAI(model="gpt-3.5-turbo")


class KnowledgeEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents = None
        self.index = None

    def create_knowledge_base(self):
        try:
            self.documents = SimpleDirectoryReader(settings.data_dir).load_data()
        except:
            logger.warning("There is no available document data.")
            return

        logger.debug("Creating knowledge base.")

        self.index = VectorStoreIndex.from_documents(self.documents)

        # save the resulting index to disk so that we can use it later
        logger.debug("Knowledge base created. Saving to disk...")
        self.index.storage_context.persist()
        logger.debug("Index created from knowledge base.")

    def load_index_from_storage(self):
        logger.debug("Loading index from storage.")
        self.index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=settings.storage_dir),
        )