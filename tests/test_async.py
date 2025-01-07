import asyncio

import pytest

from metisai.async_metis import AsyncMetisBot


@pytest.mark.asyncio
async def test_message(async_metis_bot: AsyncMetisBot, prompt: str):
    session = await async_metis_bot.create_session()
    assert session is not None
    message = await async_metis_bot.send_message(session, prompt)
    assert message is not None
    assert message.content is not None
    await async_metis_bot.delete_session(session)


@pytest.mark.asyncio
async def test_session(async_metis_bot: AsyncMetisBot, prompt: str):
    session = await async_metis_bot.create_session()
    assert session is not None
    message = await async_metis_bot.send_message(session, prompt)
    assert message is not None
    assert message.content is not None
    prompt2 = "What if he is a book lover?"
    message2 = await async_metis_bot.send_message(session, prompt2)
    assert message2 is not None
    assert message2.content is not None
    await async_metis_bot.delete_session(session)


@pytest.mark.asyncio
async def test_async_tasks(async_metis_bot: AsyncMetisBot, prompt: str):
    session = await async_metis_bot.create_session()
    assert session is not None
    task = await async_metis_bot.send_message_async(session, prompt)
    assert task is not None
    while True:
        task_result = await async_metis_bot.retrieve_async_task(session, task)
        if task_result.status == "FINISHED":
            break
        await asyncio.sleep(1)
    assert task_result.status == "FINISHED"
    assert task_result.message.content is not None
    await async_metis_bot.delete_session(session)


@pytest.mark.asyncio
async def test_stream_messages(async_metis_bot: AsyncMetisBot, prompt: str):
    session = await async_metis_bot.create_session()
    assert session is not None
    stream = async_metis_bot.stream_messages(
        session, prompt, split_criteria={"line": True}
    )
    async for message in stream:
        assert message is not None
        assert message.message is not None
        assert message.message.content is not None
    await async_metis_bot.delete_session(session)
