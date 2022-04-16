from aiohttp import ClientSession

from api.base import BaseAPI


class TelegramAPI(BaseAPI):
    def __init__(self, session: ClientSession, token: str):
        super().__init__(session)
        self._token = token

    async def send(self, chat_id: str, text: str, parse_mode: str='HTML') -> None:
        async with self._session.post(f'https://api.telegram.org/bot{self._token}/sendMessage', data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }) as resp:
            resp.raise_for_status()

    