import asyncio
import os
import unittest

from metisai.async_metis import AsyncMetisBot


class TestAsyncTapSageBot(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        api_key = os.getenv("TAPSAGE_API_KEY")
        bot_id = os.getenv("TAPSAGE_BOT_ID")
        cls.metis_bot = AsyncMetisBot(api_key, bot_id)
        cls.prompt = (
            "Suggest me a list of 5 gifts for a 30 years boy who is technology-fan."
        )

    @staticmethod
    async def async_test(test_coro):
        loop = asyncio.get_event_loop()
        return await loop.run_until_complete(test_coro)

    async def test_create_session(self):
        print("test_create_session")
        session = await self.metis_bot.create_session()
        self.assertIsNotNone(session.id)
        print(session)
        await self.metis_bot.delete_session(session)

    async def test_send_message(self):
        print("test_send_message")
        session = await self.metis_bot.create_session()
        message = await self.metis_bot.send_message(session, self.prompt)
        self.assertIsInstance(message.content, str)
        print(message.content)
        await self.metis_bot.delete_session(session)

    async def test_send_message_async(self):
        print("test_send_message_async")
        session = await self.metis_bot.create_session()
        task = await self.metis_bot.send_message_async(session, self.prompt)

        while True:
            task_result = await self.metis_bot.retrieve_async_task(session, task)
            if task_result.status == "FINISHED":
                break
            await asyncio.sleep(1)
        self.assertIsInstance(task_result.message.content, str)
        print(task_result.message.content)
        await self.metis_bot.delete_session(session)

    async def test_stream_messages(self):
        print("test_stream_messages")
        session = await self.metis_bot.create_session()
        async for message in self.metis_bot.stream_messages(
            session, self.prompt, split_criteria={"line": True}
        ):
            print(message.message.content)
        await self.metis_bot.delete_session(session)

    def test_all_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.test_create_session())
        loop.run_until_complete(self.test_send_message())
        loop.run_until_complete(self.test_send_message_async())
        loop.run_until_complete(self.test_stream_messages())


if __name__ == "__main__":
    unittest.main()
