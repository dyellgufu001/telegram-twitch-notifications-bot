from datetime import datetime
from sys import stdout

def log(text: str, time: bool=True, end: str='\n') -> None:
    strtime = ''

    if time:
        strtime = '[' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '] '
    
    print(f'{strtime}{text}', end=end)

    if end != '\n':
        stdout.flush()