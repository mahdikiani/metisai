import os
import time
import unittest

from metisai import MetisBot


class TestMetisBot(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        api_key = os.getenv("TAPSAGE_API_KEY")
        bot_id = os.getenv("TAPSAGE_BOT_ID")
        self.metis_bot = MetisBot(api_key, bot_id)
        self.prompt = "Suggest me a list of 5 gifts for a 30 years boy who is tech-fan."

    def test_message(self):
        print()
        print("test_message")
        session = self.metis_bot.create_session()
        message = self.metis_bot.send_message(session, self.prompt)
        print(message.content)
        print()
        self.metis_bot.delete_session(session)

    def test_session(self):
        print()
        print("test_session")
        session = self.metis_bot.create_session()
        message = self.metis_bot.send_message(session, self.prompt)
        print(message.content)
        prompt2 = "What if he is a book lover?"
        message2 = self.metis_bot.send_message(session, prompt2)
        print(message2.content)
        print()
        self.metis_bot.delete_session(session)

    def test_async_tasks(self):
        print()
        print("test_async_tasks")
        session = self.metis_bot.create_session()
        task = self.metis_bot.send_message_async(session, self.prompt)

        while True:
            task_result = self.metis_bot.retrieve_async_task(session, task)
            if task_result.status == "FINISHED":
                break
            time.sleep(1)
        print(task_result.message.content)
        print()
        self.metis_bot.delete_session(session)

    def test_stream_messages(self):
        print()
        print("test_stream_messages")
        session = self.metis_bot.create_session()
        stream = self.metis_bot.stream_messages(
            session, self.prompt, split_criteria={"line": True}
        )
        for message in stream:
            print(message.message.content)
        self.metis_bot.delete_session(session)


if __name__ == "__main__":
    unittest.main()
