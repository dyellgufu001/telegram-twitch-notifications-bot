from json import dump, load
from os.path import isfile
from typing import Union

class Config:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        if isfile(filename):
            self._refresh()
        else:
            self.conf = dict()
            with open(self.filename, 'w') as f:
                f.write("{}")

    def _refresh(self) -> None:
        self.conf = load(open(self.filename))

    def get_field(self, name: str) -> any:
        self._refresh()

        if name:
            return self.conf[name]
    
    def set_field(self, name: str, value: any) -> bool:
        self._refresh()

        if name:
            self.conf[name] = value
            dump(self.conf, open(self.filename, 'w'), indent=4)
            return True
        
        return False

    def get_fields(self) -> dict:
        self._refresh()

        with open(self.filename, 'r') as f:
            return load(f)
    