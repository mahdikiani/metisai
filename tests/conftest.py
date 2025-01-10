import os

import dotenv
import pytest

from metisai import AsyncMetisBot, MetisBot

dotenv.load_dotenv()


@pytest.fixture
def metis_bot():
    api_key = os.getenv("METIS_API_KEY")
    bot_id = os.getenv("METIS_BOT_ID")
    return MetisBot(api_key, bot_id)


@pytest.fixture
def prompt():
    return os.getenv("PROMPT")


@pytest.fixture
def async_metis_bot():
    api_key = os.getenv("METIS_API_KEY")
    bot_id = os.getenv("METIS_BOT_ID")
    return AsyncMetisBot(api_key, bot_id)
