from aiohttp import ClientSession, FormData

from api.base import BaseAPI
from config import Config
from util import log


class TwitchAPI(BaseAPI):
    def __init__(self, session: ClientSession, config: Config):
        super().__init__(session)
        self._config = config

    async def get_stream_data(self, user_login: str) -> None:
        async with self._session.get('https://api.twitch.tv/helix/streams', params={'user_login': user_login}, 
            headers={'Authorization': f"Bearer {self._config.get_field('twitch_token')}", 'Client-Id': self._config.get_field('twitch_client_id')
        }) as resp:
            body = await resp.json()

            if resp.status == 401 and body['message'] == 'Invalid OAuth token':
                log('Access token has expired. Refreshing:', time=False)
                await self._refresh_twitch_token()
                
            else:
                resp.raise_for_status()

            return body

    async def _refresh_twitch_token(self):
        async with self._session.post('https://id.twitch.tv/oauth2/token', data=FormData({
            'client_id': self._config.get_field('twitch_client_id'),
            'client_secret': self._config.get_field('twitch_client_secret'),
            'grant_type': 'refresh_token',
            'refresh_token': self._config.get_field('twitch_refresh_token')
        })) as resp:
            resp.raise_for_status()

            result = await resp.json()
            
            log(f'Token refreshed:\n    Access token: {result["access_token"]}\n    Refresh token: {result["refresh_token"]}')

            self._config.set_field('twitch_token', result['access_token'])
            self._config.set_field('twitch_refresh_token', result['refresh_token'])
