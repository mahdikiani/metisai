import json
import logging
import uuid

import httpx

from metisai.metistypes import (
    Attachment,
    Message,
    MessageContent,
    MessageRequest,
    MessageStream,
    Session,
    SessionRequest,
    SessionUser,
    Task,
    TaskResult,
)

logger = logging.getLogger("metis")


class AsyncMetisBot(httpx.AsyncClient):
    API_V1_SESSION = "https://api.metisai.ir/api/v1/chat/"

    def __init__(self, api_key, bot_id=None):
        self.api_key = api_key
        super().__init__(
            base_url=self.API_V1_SESSION,
            headers={"Content-Type": "application/json", "X-Api-Key": self.api_key},
        )
        self.bot_id = bot_id

    async def create_session(
        self, user_id: str | None = None, bot_id: str | None = None
    ) -> Session:
        if bot_id is None:
            bot_id = self.bot_id
        assert bot_id is not None

        if user_id is None:
            user_id = str(uuid.uuid4())
        else:
            user_id = str(user_id)

        session_request = SessionRequest(
            botId=bot_id, user=SessionUser(id=user_id, name="_")
        )

        response = await self.post(url="session", json=session_request.model_dump())
        response.raise_for_status()
        return Session(**response.json())

    async def list_sessions(
        self, user_id: str, bot_id: str | None = None
    ) -> list[Session]:
        if bot_id is None:
            bot_id = self.bot_id

        response = await self.get("sessions", timeout=None, params={"userId": user_id})
        return [
            Session(**data)
            for data in response.json()
            if not bot_id or data.get("botId") == bot_id
        ]

    async def retrieve_session(self, session_id: str) -> Session:
        response = await self.get(f"session/{session_id}", timeout=None)
        response.raise_for_status()
        return Session(**response.json())

    async def delete_session(self, session: Session) -> None:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id
        response = await self.delete(f"session/{session_id}", timeout=None)
        response.raise_for_status()

    async def send_message(self, session: Session, prompt: str) -> Message:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        data = MessageRequest(
            message=MessageContent(
                type="USER",
                content=prompt,
            )
        )
        response = await self.post(
            f"session/{session_id}/message", json=data.model_dump(), timeout=None
        )
        response.raise_for_status()
        return Message(**response.json())

    async def send_message_with_attachment(
        self,
        session: Session,
        prompt: str,
        attachment_url: str,
        attachment_type: str = "IMAGE",
    ) -> Message:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        data = MessageRequest(
            message=MessageContent(
                type="USER",
                content=prompt,
                attachments=[
                    Attachment(content=attachment_url, contentType=attachment_type)
                ],
            )
        )
        response = await self.post(
            f"session/{session_id}/message", json=data.model_dump(), timeout=None
        )
        response.raise_for_status()
        return Message(**response.json())

    async def send_message_async(self, session: Session, prompt: str) -> Task:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        data = MessageRequest(
            message=MessageContent(
                type="USER",
                content=prompt,
            )
        )
        response = await self.post(
            f"session/{session_id}/message/async", json=data.model_dump(), timeout=None
        )
        response.raise_for_status()
        return Task(**response.json())

    async def retrieve_async_task(self, session: Session, task: Task) -> TaskResult:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        if isinstance(task, (str, uuid.UUID)):
            task_id = task
        else:
            task_id = task.taskId

        response = await self.get(
            f"session/{session_id}/message/async/{task_id}", timeout=None
        )
        response.raise_for_status()
        return TaskResult(**response.json())

    async def stream_messages(
        self, session: Session, prompt: str, split_criteria: dict = None
    ):
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        data = MessageRequest(
            message=MessageContent(
                type="USER",
                content=prompt,
            )
        )

        async with self.stream(
            "POST",
            f"session/{session_id}/message/stream",
            json=data.model_dump(),
            timeout=None,
        ) as response:
            response.raise_for_status()
            buffer = ""

            async for line in response.aiter_lines():
                line = line.strip("data:").strip()
                if not line:
                    continue

                try:
                    msg = MessageStream(**json.loads(line))
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Failed to parse message: {line} - {e}")
                    continue

                if not split_criteria:
                    yield msg
                    continue

                buffer += msg.message.content
                if split_criteria.get("min-length") and len(
                    buffer
                ) >= split_criteria.get("min-length"):
                    yield MessageStream(
                        message=MessageContent(
                            type="AI", content=buffer, attachments=None
                        )
                    )
                    buffer = ""

                if split_criteria.get("splitter"):
                    for splitter in split_criteria.get("splitter"):
                        if splitter in buffer:
                            yield MessageStream(
                                message=MessageContent(
                                    type="AI",
                                    content=buffer,
                                    attachments=None,
                                )
                            )
                            buffer = ""
            if buffer:
                yield MessageStream(
                    message=MessageContent(type="AI", content=buffer, attachments=None)
                )
