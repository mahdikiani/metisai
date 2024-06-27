import requests

from .metistypes import Bot, BotRequest


class MetisUser:
    API_V1 = "https://api.metisai.ir/api/v1"

    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoints = {
            "bots": f"{self.API_V1}/bots",
            "get_bot": f"{self.API_V1}/bots/{{bot_id}}",
        }
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

    def create_bot(self, bot_data: BotRequest):
        assert isinstance(bot_data, BotRequest)
        response = requests.post(
            url=self.endpoints.get("bots"),
            headers=self.headers,
            json=bot_data.model_dump(),
        )
        return Bot(**response.json())

    def retrieve_bot(self, bot_id: str):
        response = requests.get(
            url=self.endpoints.get("get_bot").format(bot_id=bot_id),
            headers=self.headers,
        )
        return response.json()
