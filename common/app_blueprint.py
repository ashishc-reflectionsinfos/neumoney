from flask import Blueprint


class AppBP(Blueprint):
    def __init__(self, name, import_name):
        super().__init__(name, import_name)
