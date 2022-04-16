from datetime import datetime
from sys import stdout

import asyncio
import aiohttp

from config import Config


class Bot:
    def __init__(self):
        self._session = None
        self._is_live = False

        self._config = Config('config.json')

        self._user = self._config.get_field('twitch_user_login')

    def __del__(self):
        if self._session:
            asyncio.create_task(self._session.close())

    def _log(self, text, end='\n', time=True):
        strtime = ''

        if time:
            strtime = '[' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '] '
        
        print(f'{strtime}{text}', end=end)

        if end != '\n':
            stdout.flush()

    async def _get_stream_data(self):
        async with self._session.get('https://api.twitch.tv/helix/streams', params={'user_login': self._user}, 
            headers={'Authorization': f"Bearer {self._config.get_field('twitch_token')}", 'Client-Id': self._config.get_field('twitch_client_id')
        }) as resp:
            body = await resp.json()

            if resp.status == 401 and body['message'] == 'Invalid OAuth token':
                self._log('Access token has expired. Refreshing:', time=False)
                await self._refresh_twitch_token()
            else:
                resp.raise_for_status()

            return body

    async def _send_telegram_message(self, chat_id, text, parse_mode='HTML'):
        async with self._session.post(f'https://api.telegram.org/bot{self._config.get_field("telegram_token")}/sendMessage', data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }) as resp:
            resp.raise_for_status()
    
    async def _refresh_twitch_token(self):
        async with self._session.post('https://id.twitch.tv/oauth2/token', data=aiohttp.FormData({
            'client_id': self._config.get_field('twitch_client_id'),
            'client_secret': self._config.get_field('twitch_client_secret'),
            'grant_type': 'refresh_token',
            'refresh_token': self._config.get_field('twitch_refresh_token')
        })) as resp:
            resp.raise_for_status()

            result = await resp.json()
            
            self._log(f'Token refreshed:\n    Access token: {result["access_token"]}\n    Refresh token: {result["refresh_token"]}')

            self._config.set_field('twitch_token', result['access_token'])
            self._config.set_field('twitch_refresh_token', result['refresh_token'])

    async def start(self):
        self._session = aiohttp.ClientSession()
        self._is_live = False

        self._log(f'Selected user: {self._user}')

        while True:
            self._log('Polling... ', end='')

            stream_data = await self._get_stream_data()

            if 'status' in stream_data and stream_data['status'] == 401:
                if stream_data['message'] == 'Invalid OAuth token':
                    continue

            if not self._is_live:
                if stream_data['data']:
                    self._is_live = True
                    self._log(f'{self._user} is live: {stream_data["data"][0]["title"]}', time=False)

                    await self._send_telegram_message(self._config.get_field('telegram_chat_id'), f'{stream_data["data"][0]["title"]}: https://twitch.tv/{self._user}')
                else: 
                    self._log(f'{self._user} is not live', time=False)
            else:
                if not stream_data['data']:
                    self._is_live = False
                    self._log(f'{self._user} is not live', time=False)
                else:
                    self._log(f'{self._user} is live: {stream_data["data"][0]["title"]}', time=False)
            
            await asyncio.sleep(10)
    
    def run(self):
        asyncio.run(self.start())


if __name__ == '__main__':
    bot = Bot()

    bot.run()
