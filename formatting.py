from type.game import Game

def format_message(title: str, game: Game, user_login: str) -> str:
    title = title.replace(".", "\.").replace("!", "\!").replace("+", "\+")
    game_name = game.name().replace(".", "\.").replace("!", "\!").replace("+", "\+")

    return f'*{title}*: {game_name}\nhttps://www\.twitch\.tv/{user_login}'
