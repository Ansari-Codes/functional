class num(float):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = float(value)

class boolean(int):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

def echo(*args, **kwargs):
    print(*args, **kwargs)

def isNum(obj):
    if isinstance(obj, num):
        return True
