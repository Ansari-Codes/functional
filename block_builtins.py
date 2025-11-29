class BlockError(Exception):
    """Custom exception for Block language transpilation errors"""
    pass

BUILTIN_TYPES = ("str", "num", "boolean", "list", "tuple", "set", "map", "func", "none")
BUILTIN_COLLECTIONS = ("list", "tuple", "set", "map")
BUILTIN_FUNCTIONS = (
    # core
    "echo", "typeOf", "toStr", "toNum", "toList", "toTuple",
    "toSet", "toMap", "toBool", "len"
    # string
    "strToUpper", "strToLower", "strToTitle", "strToCapital",
    "strSwapCase", "strSplit", "strCount", "strEncode",
    "strStrip", "strLStrip", "strRStrip",
    "strReplace", "strStartsWith", "strEndsWith",
    "strFind", "strLen",
    # number
    "numAbs", "numRound", "numFloor", "numCeil",
    "numTrunc", "numPow", "numSqrt",
    "numClamp", "numSign",
    # list
    "listAppend", "listPop", "listLen", "listExtend", "listContains",
    # tuple
    "tupleLen", "tupleContains",
    # set
    "setAdd", "setRemove", "setContains",
    # map
    "mapGet", "mapSet", "mapKeys", "mapValues", "mapItems",
)
BUILTIN_CONSTANTS = {        
        'true': ('boolean', 'boolean(True)'),
        'false': ('boolean', 'boolean()'),
        'none': ('none', 'NONE'),
    }

class boolean(int):
    def __init__(self, value=False) -> None:
        self.value = bool(value)
    
    def __repr__(self) -> str:
        return self.value.__str__().lower()

    def __str__(self) -> str:
        return self.__repr__()

class none:
    _instance = None
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance
    def __repr__(self): return "none"
    __str__ = __repr__
    def __bool__(self): return False
    def __eq__(self, other): return other is None or isinstance(other, none)
NONE = none()

def _isString(obj, func): 
    if not isinstance(obj, str):
        raise BlockError(func.__name__ + " expects 'str'.")
    return True

def _isNum(obj, func):
    if not isinstance(obj, (int, float)):
        raise BlockError(func.__name__ + " expects 'num'.")
    return True

def _isList(obj, func):
    if not isinstance(obj, list):
        raise BlockError(func.__name__ + " expects 'list'.")
    return True

def _isTuple(obj, func):
    if not isinstance(obj, tuple):
        raise BlockError(func.__name__ + " expects 'tuple'.")
    return True

def _isSet(obj, func):
    if not isinstance(obj, set):
        raise BlockError(func.__name__ + " expects 'set'.")
    return True

def _isMap(obj, func):
    if not isinstance(obj, dict):
        raise BlockError(func.__name__ + " expects 'map'.")
    return True

def echo(*args, **kwargs):
    print(*args, **kwargs)

def typeOf(obj):
    t = 'none'
    if isinstance(obj, str): t="str"
    elif isinstance(obj, (bool, boolean, int)): t="boolean"
    elif isinstance(obj, (int, float)): t="num"
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

def toStr(obj):
    return str(obj)

def toNum(obj):
    try:
        return float(obj)
    except:
        raise BlockError("toNum: cannot convert to number.")

def toList(obj):
    if typeOf(obj) in BUILTIN_COLLECTIONS + ('str',):
        if typeOf(obj) == 'str': return [i for i in obj]
        elif typeOf(obj) == 'map': return list(obj.items())
        else: return list(obj)
    else:
        raise BlockError(f"toList: Cannot convert object of type '{typeOf(obj)}' to list!")

def toTuple(obj):
    if typeOf(obj) in BUILTIN_COLLECTIONS + ('str',):
        if typeOf(obj) == 'str': return tuple([i for i in obj])
        elif typeOf(obj) == 'map': return tuple(obj.items())
        else: return tuple(obj)
    else:
        raise BlockError(f"toTuple: Cannot convert object of type '{typeOf(obj)}' to tuplr!")

def toSet(obj):
    t = typeOf(obj)
    if t == 'set': return obj
    if t == 'str': return {ch for ch in obj}
    if t == 'list' or t == 'tuple':
        try: return set(obj)
        except TypeError: raise BlockError("toSet: elements must be hashable to convert to set.")
    if t == 'map':
        for k, v in obj.items():
            try: hash((k, v))
            except TypeError: raise BlockError("toSet: cannot convert map to set; key/value not hashable.")
        return set(obj.items())
    raise BlockError(f"toSet: Cannot convert object of type '{t}' to set!")

def toMap(obj):
    t = typeOf(obj)
    if t == 'map': return obj
    if t == 'str': return {i:ch for i, ch in enumerate(obj)}
    if t in ('list', 'tuple'):
        result = {}
        for item in obj:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise BlockError("toMap: expected (key, value) pairs.")
            key, value = item
            try: hash(key)
            except Exception: raise BlockError("toMap: key must be str, tupl or num.")
            result[key] = value
        return result
    if t == 'set': raise BlockError("toMap: cannot convert set to map due to hashability issues.")
    raise BlockError(f"toMap: Cannot convert object of type '{t}' to map!")

def toBool(obj): return boolean(obj)

# String operations
def strStrip(obj: str): 
    return obj.strip() if _isString(obj, strStrip) else ""
def strLStrip(obj: str):
    return obj.lstrip() if _isString(obj, strLStrip) else ""
def strRStrip(obj: str):
    return obj.rstrip() if _isString(obj, strRStrip) else ""
def strReplace(obj: str, old, new):
    return obj.replace(old, new) if _isString(obj, strReplace) else ""
def strStartsWith(obj: str, prefix):
    return boolean(obj.startswith(prefix)) if _isString(obj, strStartsWith) else boolean()
def strEndsWith(obj: str, suffix):
    return boolean(obj.endswith(suffix)) if _isString(obj, strEndsWith) else boolean()
def strFind(obj: str, substring):
    return obj.find(substring) if _isString(obj, strFind) else -1
def strLen(obj: str):
    return len(obj) if _isString(obj, strLen) else 0
def strToUpper(obj):
    return obj.upper() if _isString(obj, strToUpper) else ""
def strToLower(obj):
    return obj.lower() if _isString(obj, strToLower) else ""
def strToTitle(obj):
    return obj.title() if _isString(obj, strToTitle) else ""
def strToCapital(obj):
    if _isString(obj, strToCapital):
        return obj.capitalize()
    return ""
def strSwapCase(obj):
    return obj.swapcase() if _isString(obj, strSwapCase) else ""
def strSplit(obj, sep=None):
    return obj.split(sep) if _isString(obj, strSplit) else []
def strCount(obj, sub):
    return obj.count(sub) if _isString(obj, strCount) else 0
def strEncode(obj, encoding='utf-8'):
    if _isString(obj, strEncode):
        try:
            return str(obj.encode(encoding))
        except Exception:
            raise BlockError(f"strEncode: invalid encoding '{encoding}'.")
    return ""

# Number Operations
def numAbs(x):
    return abs(x) if _isNum(x, numAbs) else 0
def numRound(x, ndigits=0):
    return round(x, int(ndigits)) if _isNum(x, numRound) else 0
def numFloor(x):
    if _isNum(x, numFloor):
        import math
        return math.floor(x)
def numCeil(x):
    if _isNum(x, numCeil):
        import math
        return math.ceil(x)
def numTrunc(x):
    if _isNum(x, numTrunc):
        import math
        return math.trunc(x)
def numPow(a, b):
    if _isNum(a, numPow) and _isNum(b, numPow):
        return a ** b
def numSqrt(x):
    if _isNum(x, numSqrt):
        import math
        if x < 0:
            raise BlockError("numSqrt: cannot sqrt negative number.")
        return math.sqrt(x)
def numClamp(x, lo, hi):
    if _isNum(x, numClamp) and _isNum(lo, numClamp) and _isNum(hi, numClamp):
        return max(lo, min(x, hi))
def numSign(x):
    return (-1 if x < 0 else (1 if x > 0 else 0)) if _isNum(x, numSign) else 0

# List operations
def listAppend(lst, value):
    if _isList(lst, listAppend):
        lst.append(value)
        return lst
def listPop(lst, index=-1):
    if _isList(lst, listPop):
        return lst.pop(index)
def listLen(lst):
    return len(lst) if _isList(lst, listLen) else 0
def listExtend(lst, items):
    if _isList(lst, listExtend) and isinstance(items, list):
        lst.extend(items)
        return lst
def listContains(lst, value):
    return boolean(value in lst) if _isList(lst, listContains) else boolean()

# Tuple operations
def tupleLen(t):
    return len(t) if _isTuple(t, tupleLen) else 0
def tupleContains(t, value):
    return boolean(value in t) if _isTuple(t, tupleContains) else boolean()

# Set operations
def setAdd(s, value):
    if _isSet(s, setAdd):
        s.add(value)
        return s
def setRemove(s, value):
    if _isSet(s, setRemove):
        s.remove(value)
        return s
def setContains(s, value):
    return boolean(value in s) if _isSet(s, setContains) else boolean()

# Map operations
def mapGet(m, key, default=None):
    return m.get(key, default) if _isMap(m, mapGet) else none()
def mapSet(m, key, value):
    if _isMap(m, mapSet):
        m[key] = value
        return m
def mapKeys(m):
    return list(m.keys()) if _isMap(m, mapKeys) else []
def mapValues(m):
    return list(m.values()) if _isMap(m, mapValues) else []
def mapItems(m):
    return list(m.items()) if _isMap(m, mapItems) else []
