import asyncio
from aiohttp import ClientSession

from config import Config
from api.telegram import TelegramAPI
from api.twitch import TwitchAPI
from formatting import format_message
from type.game import Game
from util import log


class Bot:
    def __init__(self) -> None:
        self._session = None
        self._is_live = False

        self._game = None
        self._stream_title = None
        self._last_message_id = None

        self._telegram = None
        self._twitch = None

        self._config = Config('../config.json')

        self._chat_id = self._config.get_field('telegram_chat_id')
        self._user = self._config.get_field('twitch_user_login')

        self._polling_interval = self._config.get_field("polling_interval")

    def __del__(self) -> None:
        if self._session:
            asyncio.create_task(self._session.close())

    async def start(self) -> None:
        self._session = ClientSession()
            
        self._telegram = TelegramAPI(self._session, self._config.get_field("telegram_token"))
        self._twitch = TwitchAPI(self._session, self._config)
        
        self._is_live = False

        log(f'Selected user: {self._user}')

        while True:
            log('Polling... ', end='')

            stream_data = await self._twitch.get_stream_data(self._user)

            if 'status' in stream_data and stream_data['status'] == 401:
                if stream_data['message'] == 'Invalid OAuth token':
                    continue

            if not self._is_live:
                if stream_data['data']:
                    self._is_live = True
                    log(f'{self._user} is live: {stream_data["data"][0]["title"]}', time=False)

                    self._stream_title = stream_data["data"][0]["title"]
                    self._game = Game(stream_data["data"][0]["game_id"], stream_data["data"][0]["game_name"])

                    message = await self._telegram.send_message(self._chat_id, format_message(self._stream_title, self._game, self._user), disable_web_page_preview=True)
                    self._last_message_id = message["result"]["message_id"]

                else: 
                    log(f'{self._user} is not live', time=False)

            else:
                if not stream_data['data']:
                    self._is_live = False
                    log(f'{self._user} is not live', time=False)

                else:
                    log(f'{self._user} is live: {stream_data["data"][0]["title"]}', time=False)

                    if stream_data["data"][0]["title"] != self._stream_title or stream_data["data"][0]["game_id"] != self._game.id():
                        self._stream_title = stream_data["data"][0]["title"]
                        self._game = Game(stream_data["data"][0]["game_id"], stream_data["data"][0]["game_name"])

                        await self._telegram.edit_message_text(self._chat_id, self._last_message_id, format_message(self._stream_title, self._game, self._user), disable_web_page_preview=True)
            
            await asyncio.sleep(self._polling_interval)
    
    def run(self) -> None:
        asyncio.run(self.start())


if __name__ == '__main__':
    bot = Bot()

    bot.run()
