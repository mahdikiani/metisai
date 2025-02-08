import json
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


class MetisBot(httpx.Client):
    API_V1_SESSION = "https://api.metisai.ir/api/v1/chat"

    def __init__(self, api_key, bot_id: str | None = None):
        super().__init__(
            base_url=self.API_V1_SESSION,
            headers={"Content-Type": "application/json", "X-Api-Key": api_key},
        )
        self.bot_id = bot_id

    def create_session(
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

        response = self.post(url="session", json=session_request.model_dump())
        response.raise_for_status()
        return Session(**response.json())

    def list_sessions(self, user_id: str, bot_id: str | None = None) -> list[Session]:
        if bot_id is None:
            bot_id = self.bot_id

        response = self.get("sessions", timeout=None, params={"userId": user_id})
        response.raise_for_status()
        return [
            Session(**data)
            for data in response.json()
            if not bot_id or data.get("botId") == bot_id
        ]

    def retrieve_session(self, session_id: str) -> Session:
        response = self.get(f"session/{session_id}", timeout=None)
        response.raise_for_status()
        return Session(**response.json())

    def delete_session(self, session: Session) -> None:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        response = self.delete(f"session/{session_id}", timeout=None)
        response.raise_for_status()

    def send_message(self, session: Session | str | uuid.UUID, prompt: str) -> Message:
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
        response = self.post(
            f"session/{session_id}/message", json=data.model_dump(), timeout=None
        )
        response.raise_for_status()
        return Message(**response.json())

    def send_message_with_attachment(
        self,
        session: Session | str | uuid.UUID,
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
        response = self.post(
            f"session/{session_id}/message", json=data.model_dump(), timeout=None
        )
        response.raise_for_status()
        return Message(**response.json())

    def send_message_async(self, session: Session, prompt: str) -> Task:
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
        response = self.post(
            f"session/{session_id}/message/async", json=data.model_dump(), timeout=None
        )
        response.raise_for_status()
        return Task(**response.json())

    def retrieve_async_task(self, session: Session, task: Task) -> TaskResult:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        if isinstance(task, (str, uuid.UUID)):
            task_id = task
        else:
            task_id = task.taskId

        response = self.get(
            f"session/{session_id}/message/async/{task_id}", timeout=None
        )
        response.raise_for_status()
        return TaskResult(**response.json())

    def stream_messages(
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
        with self.stream(
            "POST",
            f"session/{session_id}/message/stream",
            json=data.model_dump(),
            timeout=None,  # stream=True
        ) as response:
            # response.raise_for_status()

            if split_criteria.get("words"):
                split_criteria["splitter"] = " "
            elif split_criteria.get("sentence"):
                split_criteria["splitter"] = ".?!:"
            elif split_criteria.get("line"):
                split_criteria["splitter"] = "\n"

            buffer = ""
            for line in response.iter_lines():
                if line:
                    data = line.replace("data:", "")
                    msg = MessageStream(**json.loads(data))
                    if not split_criteria:
                        yield MessageStream(**json.loads(data))
                        continue

                    buffer += msg.message.content
                    if split_criteria.get("min-length"):
                        if len(buffer) >= split_criteria.get("min-length"):
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
                                        type="AI", content=buffer, attachments=None
                                    )
                                )
                                buffer = ""

            yield MessageStream(
                message=MessageContent(type="AI", content=buffer, attachments=None)
            )
