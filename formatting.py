from re import sub
from type.game import Game

def format_message(title: str, game: Game, user_login: str) -> str:
    title = sub(r"([_*[\]()~`>#+\-=|{}.!])", r"\\\1", title)
    game_name = sub(r"([_*[\]()~`>#+\-=|{}.!])", r"\\\1", game.name())

    return f'*{title}*: {game_name}\nhttps://www\.twitch\.tv/{user_login}'
