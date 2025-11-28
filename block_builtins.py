class BlockError(Exception):
    """Custom exception for Block language transpilation errors"""
    pass

BUILTIN_TYPES = ("str", "num", "boolean", "list", "tuple", "set", "map", "func", "none")
BUILTIN_FUNCTIONS = ("echo", "typeOf", "toStr", "toNum")
BUILTIN_CONSTANTS = {        
        'true': ('boolean', 'boolean(True)'),
        'false': ('boolean', 'boolean()'),
        'none': ('str', 'none()'),
    }

class boolean(int):
    def __init__(self, value=False) -> None:
        self.value = bool(value)
    
    def __repr__(self) -> str:
        return self.value.__str__().lower()

    def __str__(self) -> str:
        return self.__repr__()
class none:
    def __repr__(self) -> str:
        return "none"
    def __str__(self) -> str:
        return self.__repr__()

def echo(*args, **kwargs):
    print(*args, **kwargs)

def typeOf(obj):
    t = 'none'
    if isinstance(obj, str): t="str"
    elif isinstance(obj, (int, float)): t="num"
    elif isinstance(obj, (bool)): t="boolean"
    elif isinstance(obj, list): t="list"
    elif isinstance(obj, tuple): t="tuple"
    elif isinstance(obj, set): t="set"
    elif isinstance(obj, dict): t="map"
    elif getattr(
            getattr(
                obj,
                "__class__", {}
                ),
            "__name__",  ""
        ).__contains__("function"): t="func"
    return f"{t}"

# String operations
def toStr(obj): return f"{obj!r}"

# Number Operations
def toNum(obj):
    convertable_types = ['str', 'none', 'boolean', 'num']
    if typeOf(obj) not in convertable_types:
        raise BlockError(f"Given type '{typeOf(obj)}' is not castable to 'num'.")
    elif typeOf(obj) == 'str':
        try:
            float(obj)
        except TypeError:
            raise BlockError(f"Non-numeric string is not castable to 'num'.")
    return float(obj)

