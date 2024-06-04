import re
import unicodedata


class NameRegulator:
    def __init__(self):
        pass

    def normalize(self, name: str) -> str:
        if not isinstance(name, str):
            return ''
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
        name = name.lower().strip()
        name = re.sub(r'[^a-z0-9 ]', '', name)
        name = re.sub(r'\s+', ' ', name)

        return name


if __name__ == "__main__":
    regulator = NameRegulator()
