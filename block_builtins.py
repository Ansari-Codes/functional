class BlockError(Exception):
    """Custom exception for Block language transpilation errors"""
    pass

BUILTIN_TYPES = ("str", "num", "boolean", "list", "tuple", "set", "map", "func", "none")
BUILTIN_FUNCTIONS = (
    # core
    "echo", "typeOf", "toStr", "toNum",
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

def toStr(obj):
    return str(obj)

def toNum(obj):
    try:
        return float(obj)
    except:
        raise BlockError("toNum: cannot convert to number.")

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
            return obj.encode(encoding)
        except Exception:
            raise BlockError(f"strEncode: invalid encoding '{encoding}'.")
    return b""

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
