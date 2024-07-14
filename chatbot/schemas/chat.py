from llama_index.core.llms import MessageRole
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: MessageRole
    content: str

class ChatData(BaseModel):
    messages: list[ChatMessage]


class ChatResult(BaseModel):
    result: ChatMessage