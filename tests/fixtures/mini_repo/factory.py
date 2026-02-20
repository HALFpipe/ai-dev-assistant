from .adapter import Factory


class AdapterFactory(Factory):
    def get(self, name: str):
        return f"adapter:{name}"
