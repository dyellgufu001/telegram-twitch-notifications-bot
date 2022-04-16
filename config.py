from json import dump, load
from os.path import isfile

class Config:
    def __init__(self, filename: str):
        self.filename = filename
        if isfile(filename):
            self.__refresh()
        else:
            self.conf = dict()
            with open(self.filename, 'w') as f:
                f.write("{}")

    def __refresh(self):
        self.conf = load(open(self.filename))

    def get_field(self, name: str):
        self.__refresh()

        if name:
            return self.conf[name]
    
    def set_field(self, name: str, value: any):
        self.__refresh()

        if name:
            self.conf[name] = value
            dump(self.conf, open(self.filename, 'w'), indent=4)
            return True
        
        return False

    def get_fields(self):
        self.__refresh()

        with open(self.filename, 'r') as f:
            return f.read()
    