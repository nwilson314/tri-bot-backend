from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.openai import OpenAI
from loguru import logger

from chatbot.settings import settings


class KnowledgeEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents = None
        self.index = None
        self.chat_engine = None

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

    def create_chat_engine(self):
        logger.debug("Creating chat engine.")
        llm = OpenAI(model="gpt-3.5-turbo")
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="condense_plus_context",
            llm=llm,
            context_prompt=(
                "You are a knowledge assistant. Your primary area of expertise is in triathlon training, nutrition, and planning. Please always provide a detailed answer and prioritize giving usesful and precise advice/information."
                " Here are some relevant documents: {context_str}"
                "\n Instruction: Based on the above documents, please provide an answer for the user question below."
            ),
            verbose=True if settings.environment == "dev" else False,
        )