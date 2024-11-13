from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str  # Email
    firstName: str
    lastName: str
    activated: bool = False


class APIKey(BaseModel):
    id: str
    apiKey: str
    userId: str
    # description: str


class Provider(BaseModel):
    name: str
    model: str


class ProviderConfig(BaseModel):
    provider: Provider
    args: dict[str, Any]


class ChatProvider(BaseModel):
    name: str
    model: str
    currency: str
    fixedCallPrice: float
    inputTokenUnitPrice: float
    outputTokenUnitPrice: float


class Summarizer(BaseModel):
    provider: Provider
    args: dict[str, Any]


class BotRequest(BaseModel):
    name: str
    instructions: str
    providerConfig: ProviderConfig
    corpusIds: list[str]
    summarizer: Summarizer
    functions: list[str]
    description: str
    avatar: str
    enabled: bool


class Bot(BaseModel):
    id: str
    name: str
    userId: str
    instructions: str | None = None
    externalId: str
    providerConfig: ProviderConfig
    chatProvider: ChatProvider
    corpora: list[
        str
    ]  # Adjust the type if the corpora list contains more complex objects.
    summarizer: Summarizer
    functions: list[str]  # Adjust if functions contain more complex objects.
    description: str | None = None
    avatar: str | None = None
    enabled: bool = False


class Attachment(BaseModel):
    content: str
    contentType: str


class MessageContent(BaseModel):
    type: Literal["USER", "AI"]
    content: str
    attachments: list[Attachment] | None = None


class ExternalUser(BaseModel):
    id: str
    name: str


class BotInfo(BaseModel):
    botId: str
    sessionId: str


class MessageRequest(BaseModel):
    message: MessageContent


class Message(BaseModel):
    id: str
    type: Literal["USER", "AI"]
    content: str | None = None
    attachments: list[Attachment] | None = None
    timestamp: datetime
    finishReason: Literal["STOP", "LENGTH", "CONTENT_FILTER"] | None


class MessageStream(BaseModel):
    message: MessageContent


class Task(BaseModel):
    taskId: str


class TaskResult(BaseModel):
    status: Literal["RUNNING", "FINISHED", "FAILED"]
    message: Message | None = None
    percentage: int | None = None


class SessionUser(BaseModel):
    id: str | None = None
    name: str | None = None


class SessionRequest(BaseModel):
    botId: str | None = None
    user: SessionUser | None = None
    initialMessages: list[MessageContent] = []


class Session(BaseModel):
    id: str
    botId: str
    user: SessionUser
    messages: list[Message]
    startDate: datetime
