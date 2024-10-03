import json
import uuid

import aiohttp

from ..metistypes import (
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


class AsyncMetisBot:
    API_V1_SESSION = "https://api.metisai.ir/api/v1/chat/session"

    def __init__(self, api_key, bot_id):
        self.api_key = api_key
        self.endpoints = {
            "sessions": f"{self.API_V1_SESSION}s?userId={{user_id}}",
            "session": f"{self.API_V1_SESSION}",
            "get_session": f"{self.API_V1_SESSION}/{{session_id}}",
            "message": f"{self.API_V1_SESSION}/{{session_id}}/message",
            "async_task": f"{self.API_V1_SESSION}/{{session_id}}/message/async",
            "get_async_task": f"{self.API_V1_SESSION}/{{session_id}}/message/async/{{task_id}}",
            "stream": f"{self.API_V1_SESSION}/{{session_id}}/message/stream",
        }
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        self.bot_id = bot_id

    async def _request(self, method: str, endpoint: str, **kwargs):
        url = self.endpoints.get(endpoint).format(**kwargs.pop("url_params", {}))
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, **kwargs
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def create_session(self, user_id: str = None) -> Session:
        if user_id is None:
            user_id = str(uuid.uuid4())

        session_request = SessionRequest(
            botId=self.bot_id, user=SessionUser(id=user_id, name="_")
        )

        response_data = await self._request(
            method="POST",
            endpoint="session",
            json=session_request.model_dump(),
        )
        return Session(**response_data)

    async def list_sessions(self, user_id: str) -> list[Session]:
        response_data = await self._request(
            method="GET", endpoint="sessions", url_params={"user_id": user_id}
        )
        return [Session(**data) for data in response_data]

    async def retrieve_session(self, session_id: str) -> Session:
        response_data = await self._request(
            method="GET",
            endpoint="get_session",
            url_params={"session_id": session_id},
        )
        return Session(**response_data)

    async def delete_session(self, session: Session) -> None:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id
        await self._request(
            method="DELETE",
            endpoint="get_session",
            url_params={"session_id": session_id},
        )

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
        response_data = await self._request(
            method="POST",
            endpoint="message",
            url_params={"session_id": session_id},
            json=data.model_dump(),
        )
        return Message(**response_data)

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
        response_data = await self._request(
            method="POST",
            endpoint="async_task",
            url_params={"session_id": session_id},
            json=data.model_dump(),
        )
        return Task(**response_data)

    async def retrieve_async_task(self, session: Session, task: Task) -> TaskResult:
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        if isinstance(task, (str, uuid.UUID)):
            task_id = task
        else:
            task_id = task.taskId

        response_data = await self._request(
            method="GET",
            endpoint="get_async_task",
            url_params={"session_id": session_id, "task_id": task_id},
        )
        return TaskResult(**response_data)

    async def stream_messages(
        self, session: Session, prompt: str, split_criteria: dict = None
    ):
        if isinstance(session, (str, uuid.UUID)):
            session_id = session
        else:
            session_id = session.id

        url = self.endpoints.get("stream").format(session_id=session_id)
        data = MessageRequest(
            message=MessageContent(
                type="USER",
                content=prompt,
            )
        )

        async with aiohttp.ClientSession() as _session:
            async with _session.post(
                url, headers=self.headers, json=data.model_dump()
            ) as response:
                response.raise_for_status()
                buffer = ""

                async for line in response.content:
                    if line:
                        data = line.decode("utf-8").strip("data:").strip()
                        if not data:
                            continue
                        msg = MessageStream(**json.loads(data))
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

                yield MessageStream(
                    message=MessageContent(type="AI", content=buffer, attachments=None)
                )

    async def close(self):
        if self._session is not None:
            await self._session.close()
            self._session = None
