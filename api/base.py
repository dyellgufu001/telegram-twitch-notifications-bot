from aiohttp import ClientSession


class BaseAPI:
    def __init__(self, session: ClientSession):
        self._session = session
