class Client(object):
    def __init__(self, base_url: str) -> None:
        self.__base_url = base_url

    @property
    def base_url(self) -> str:
        return self.__base_url
