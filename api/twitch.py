from aiohttp import ClientSession, FormData

from api.base import BaseAPI
from config import Config
from util import log


class TwitchAPI(BaseAPI):
    def __init__(self, session: ClientSession, config: Config, debug=False):
        super().__init__(session)

        self.__config = config
        self.__debug = debug

    async def get_stream_data(self, user_login: str) -> None:
        if self.__config.get_field('twitch_token') == '':
            await self.__generate_twitch_token()
        
        async with self._session.get('https://api.twitch.tv/helix/streams', params={'user_login': user_login}, 
            headers={'Authorization': f"Bearer {self.__config.get_field('twitch_token')}", 'Client-Id': self.__config.get_field('twitch_client_id')
        }) as resp:
            body = await resp.json()

            if resp.status == 401 and body['message'] == 'Invalid OAuth token':
                log('Access token has expired. Refreshing:', time=False)
                await self.__refresh_twitch_token()
                
            else:
                if self.__debug:
                    print(await resp.text())
                resp.raise_for_status()

            return body
    
    async def __generate_twitch_token(self):
        async with self._session.get('https://id.twitch.tv/oauth2/authorize', allow_redirects=True, params={
            'response_type': 'code',
            'client_id': self.__config.get_field('twitch_client_id'),
            'redirect_uri': 'http://localhost:3000/',
            'scope': 'openid chat:read chat:edit whispers:read whispers:edit'
        }) as resp:
            if self.__debug:
                print(resp.url.relative().query)
            resp.raise_for_status()

    async def __refresh_twitch_token(self):
        async with self._session.post('https://id.twitch.tv/oauth2/token', data=FormData({
            'client_id': self.__config.get_field('twitch_client_id'),
            'client_secret': self.__config.get_field('twitch_client_secret'),
            'grant_type': 'refresh_token',
            'refresh_token': self.__config.get_field('twitch_refresh_token')
        })) as resp:
            if self.__debug:
                print(await resp.text())
            resp.raise_for_status()

            result = await resp.json()
            
            log(f'Token refreshed:\n    Access token: {result["access_token"]}\n    Refresh token: {result["refresh_token"]}')

            self.__config.set_field('twitch_token', result['access_token'])
            self.__config.set_field('twitch_refresh_token', result['refresh_token'])
