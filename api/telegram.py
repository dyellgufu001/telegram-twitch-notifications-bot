from aiohttp import ClientSession

from api.base import BaseAPI


class TelegramAPI(BaseAPI):
    def __init__(self, session: ClientSession, token: str, debug=False):
        super().__init__(session)
        
        self.__token = token
        self.__debug = debug

    async def send_message(self, chat_id: str, text: str, parse_mode: str='MarkdownV2', disable_web_page_preview: bool=False) -> None:
        async with self._session.post(f'https://api.telegram.org/bot{self.__token}/sendMessage', data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }) as resp:
            if self.__debug:
                print(await resp.text())
            resp.raise_for_status()

            return await resp.json()
    
    async def edit_message_text(self, chat_id: str, message_id: int, text: str, parse_mode: str='MarkdownV2', disable_web_page_preview: bool=False) -> None:
        async with self._session.post(f'https://api.telegram.org/bot{self.__token}/editMessageText', data={
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }) as resp:
            if self.__debug:
                print(await resp.text())
            resp.raise_for_status()

            return await resp.json()
