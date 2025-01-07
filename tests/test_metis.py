import time

from metisai import MetisBot


def test_message(metis_bot: MetisBot, prompt: str):
    session = metis_bot.create_session()
    assert session is not None
    message = metis_bot.send_message(session, prompt)
    assert message is not None
    assert message.content is not None
    metis_bot.delete_session(session)


def test_session(metis_bot: MetisBot, prompt: str):
    session = metis_bot.create_session()
    assert session is not None
    message = metis_bot.send_message(session, prompt)
    assert message is not None
    assert message.content is not None
    prompt2 = "What if he is a book lover?"
    message2 = metis_bot.send_message(session, prompt2)
    assert message2 is not None
    assert message2.content is not None
    metis_bot.delete_session(session)


def test_async_tasks(metis_bot: MetisBot, prompt: str):
    session = metis_bot.create_session()
    assert session is not None
    task = metis_bot.send_message_async(session, prompt)
    assert task is not None
    while True:
        task_result = metis_bot.retrieve_async_task(session, task)
        if task_result.status == "FINISHED":
            break
        time.sleep(1)
    assert task_result.status == "FINISHED"
    assert task_result.message.content is not None
    metis_bot.delete_session(session)


def test_stream_messages(metis_bot: MetisBot, prompt: str):
    session = metis_bot.create_session()
    assert session is not None
    stream = metis_bot.stream_messages(session, prompt, split_criteria={"line": True})
    for message in stream:
        assert message is not None
        assert message.message is not None
        assert message.message.content is not None
    metis_bot.delete_session(session)
