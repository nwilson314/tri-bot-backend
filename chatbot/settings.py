from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "dev"
    openai_api_key: str
    data_path: str = "data"
    create_knowledge_base: bool = False
    storage_dir: str = "./storage"  # directory to cache the generated index
    data_dir: str = "./data"  # directory containing the documents to index

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()