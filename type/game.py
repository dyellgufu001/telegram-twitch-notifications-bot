class Game:
    def __init__(self, game_id: str, game_name: str) -> None:
        self.__game_id = game_id
        self.__game_name = game_name
    
    def id(self) -> str:
        return self.__game_id
    
    def name(self) -> str:
        return self.__game_name