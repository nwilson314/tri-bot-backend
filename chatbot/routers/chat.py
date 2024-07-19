from fastapi import APIRouter, Depends, HTTPException, status
from llama_index.core.llms import ChatMessage as LLMChatMessage, MessageRole
from loguru import logger

from chatbot.engine import KnowledgeEngine, get_knowledge_engine_dep
from chatbot.schemas.chat import ChatData, ChatMessage, ChatResult

router = APIRouter()


@router.post("/chat")
async def chat(
    data: ChatData, knowledge_engine: KnowledgeEngine = Depends(get_knowledge_engine_dep)
) -> ChatResult:
    # check preconditions and get last message
    logger.debug(f"received messages: {data}")
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        LLMChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    # query chat engine
    response = knowledge_engine.chat_engine.chat(lastMessage.content, messages)
    return ChatResult(
        result=ChatMessage(role=MessageRole.ASSISTANT, content=response.response)
    )
