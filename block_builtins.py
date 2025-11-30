import sys, math
class BlockError(Exception):
    """Custom exception for Block language transpilation errors"""
    pass

BUILTIN_TYPES = ("str", "num", "boolean", "list", "tuple", "set", "map", "func", "none")
BUILTIN_COLLECTIONS = ("list", "tuple", "set", "map", "str")
BUILTIN_FUNCTIONS = ['exit']
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

def builtin(func):
    BUILTIN_FUNCTIONS.append(func.__name__)
    return func

@builtin
def echo(*args, **kwargs): print(*args, **kwargs)

@builtin
def typeOf(obj):
    t = 'none'
    if isinstance(obj, str): return "str"
    if isinstance(obj, boolean): return "boolean"
    if isinstance(obj, bool): return "boolean"
    if isinstance(obj, (int, float)): return "num"
    if isinstance(obj, list): return "list"
    if isinstance(obj, tuple): return "tuple"
    if isinstance(obj, set): return "set"
    if isinstance(obj, dict): return "map"
    if callable(obj): return "func"
    if getattr(
            getattr(
                obj,
                "__class__", {}
                ),
            "__name__",  ""
        ).__contains__("function"): t="func"
    return f"{t}"

@builtin
def lenOf(obj):
    if typeOf(obj) in BUILTIN_COLLECTIONS: return len(obj)
    else: raise BlockError(f"lenOf: requires one of {', '.join(BUILTIN_COLLECTIONS)}")

@builtin
def toStr(obj): return str(obj)

@builtin
def toNum(obj):
    try: return float(obj)
    except: raise BlockError("toNum: cannot convert to number.")

@builtin
def toList(obj):
    if typeOf(obj) in BUILTIN_COLLECTIONS:
        if typeOf(obj) == 'str': return [i for i in obj]
        elif typeOf(obj) == 'map': return list(obj.items())
        else: return list(obj)
    else: raise BlockError(f"toList: Cannot convert object of type '{typeOf(obj)}' to list!")

@builtin
def toTuple(obj):
    if typeOf(obj) in BUILTIN_COLLECTIONS:
        if typeOf(obj) == 'str': return tuple([i for i in obj])
        elif typeOf(obj) == 'map': return tuple(obj.items())
        else: return tuple(obj)
    else: raise BlockError(f"toTuple: Cannot convert object of type '{typeOf(obj)}' to tuplr!")

@builtin
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

@builtin
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
            except Exception: raise BlockError("toMap: key must be str, tuple or num.")
            result[key] = value
        return result
    if t == 'set': raise BlockError("toMap: cannot convert set to map due to hashability issues.")
    raise BlockError(f"toMap: Cannot convert object of type '{t}' to map!")

@builtin
def toBool(obj): return boolean(obj)

# String operations
@builtin
def strStrip(obj: str): return obj.strip() if _isString(obj, strStrip) else ""
@builtin
def strLStrip(obj: str): return obj.lstrip() if _isString(obj, strLStrip) else ""
@builtin
def strRStrip(obj: str): return obj.rstrip() if _isString(obj, strRStrip) else ""
@builtin
def strReplace(obj: str, old, new): return obj.replace(old, new) if _isString(obj, strReplace) else ""
@builtin
def strStartsWith(obj: str, prefix): return boolean(obj.startswith(prefix)) if _isString(obj, strStartsWith) else boolean()
@builtin
def strEndsWith(obj: str, suffix): return boolean(obj.endswith(suffix)) if _isString(obj, strEndsWith) else boolean()
@builtin
def strFind(obj: str, substring): return obj.find(substring) if _isString(obj, strFind) else -1
@builtin
def strLen(obj: str): return len(obj) if _isString(obj, strLen) else 0
@builtin
def strToUpper(obj): return obj.upper() if _isString(obj, strToUpper) else ""
@builtin
def strToLower(obj): return obj.lower() if _isString(obj, strToLower) else ""
@builtin
def strToTitle(obj): return obj.title() if _isString(obj, strToTitle) else ""
@builtin
def strToCapital(obj):
    if _isString(obj, strToCapital): return obj.capitalize()
    return ""
@builtin
def strSwapCase(obj): return obj.swapcase() if _isString(obj, strSwapCase) else ""
@builtin
def strSplit(obj, sep=None): return obj.split(sep) if _isString(obj, strSplit) else []
@builtin
def strCount(obj, sub): return obj.count(sub) if _isString(obj, strCount) else 0
@builtin
def strEncode(obj, encoding='utf-8'):
    if _isString(obj, strEncode):
        try: return str(obj.encode(encoding))
        except Exception: raise BlockError(f"strEncode: invalid encoding '{encoding}'.")
    return ""

# Number Operations
@builtin
def numAbs(x): return abs(x) if _isNum(x, numAbs) else 0
@builtin
def numRound(x, ndigits=0): return round(x, int(ndigits)) if _isNum(x, numRound) else 0
@builtin
def numFloor(x):
    if _isNum(x, numFloor): return math.floor(x)
@builtin
def numCeil(x):
    if _isNum(x, numCeil): return math.ceil(x)
@builtin
def numTrunc(x):
    if _isNum(x, numTrunc): return math.trunc(x)
@builtin
def numPow(a, b, mod=None):
    if _isNum(a, numPow) and _isNum(b, numPow):
        if mod is None:return pow(a, b)
        else:
            try:return pow(int(a), int(b), int(mod))
            except Exception: raise BlockError(
                "numPow: for modulus variant, a, b, mod must be integer-convertible."
                )
@builtin
def numSqrt(x):
    if _isNum(x, numSqrt):
        if x < 0: return (0, math.sqrt(abs(x)))
        return math.sqrt(x)
@builtin
def numCbrt(x):
    if _isNum(x, numCbrt): return math.cbrt(x)
@builtin
def numClamp(x, lo, hi):
    if _isNum(x, numClamp) and _isNum(lo, numClamp) and _isNum(hi, numClamp): return max(lo, min(x, hi))
@builtin
def numSign(x): return (-1 if x < 0 else (1 if x > 0 else 0)) if _isNum(x, numSign) else 0
@builtin
def numMin(x, y): return min(x, y)
@builtin
def numMax(x, y): return max(x, y)
@builtin
def numBin(x): return bin(x)
@builtin
def numOct(x): return oct(x)
@builtin
def numHex(x): return hex(x)

# List operations
@builtin
def listAppend(lst, value):
    if _isList(lst, listAppend):
        lst.append(value)
        return lst
@builtin
def listPop(lst, index=-1):
    if _isList(lst, listPop): return lst.pop(index)
@builtin
def listExtend(lst, items):
    if _isList(lst, listExtend) and isinstance(items, list):
        lst.extend(items)
        return lst

# Set operations
@builtin
def setAdd(s, value):
    if _isSet(s, setAdd):
        s.add(value)
        return s
@builtin
def setRemove(s, value):
    if _isSet(s, setRemove):
        s.remove(value)
        return s

# Map operations
@builtin
def mapGet(m, key, default=None): return m.get(key, default) if _isMap(m, mapGet) else none()
@builtin
def mapSet(m, key, value):
    if _isMap(m, mapSet):
        m[key] = value
        return m
@builtin
def mapKeys(m):
    return list(m.keys()) if _isMap(m, mapKeys) else []
@builtin
def mapValues(m):
    return list(m.values()) if _isMap(m, mapValues) else []
@builtin
def mapItems(m):
    return list(m.items()) if _isMap(m, mapItems) else []

# Collection Specific
@builtin
def colIsEmtpy(obj):
    if typeOf(obj) not in BUILTIN_COLLECTIONS: 
        raise BlockError(f"isEmtpy requires an obj of type {', '.join([i for i in BUILTIN_COLLECTIONS])}.")
    return boolean(len(obj) == 0)

@builtin
def colOfNums(start=0, stop=0, step=1, func=toNum):
    try:
        start_i = int(start)
        stop_i = int(stop)
        step_i = int(step)
    except Exception:
        raise BlockError("colOfNums: start, stop and step must be integers.")
    if step_i == 0: raise BlockError("colOfNums: step must not be zero.")
    return tuple([func(i) for i in range(start_i, stop_i + step_i, step_i)])

@builtin
def colFilter(obj, func):
    if typeOf(obj) in BUILTIN_COLLECTIONS:
        if typeOf(obj) == 'map':
            return toMap({k:v for k,v in obj.items() if func(k,v)})
        elif typeOf(obj) == 'list':
            return [i for i in obj if func(i)]
        elif typeOf(obj) == 'tuple':
            return (i for i in obj if func(i))
        elif typeOf(obj) == 'set':
            return {i for i in obj if func(i)}
        elif typeOf(obj) == 'str':
            return ''.join([i for i in obj if func(i)])
    else:
        raise BlockError(f"colFilter only accepts one of {', '.join([i for i in BUILTIN_COLLECTIONS])}.")

@builtin
def colApplyF(obj, func):
    if typeOf(obj) in BUILTIN_COLLECTIONS:
        if typeOf(obj) == 'map':
            return toMap({k:func(v) for k,v in obj.items()})
        elif typeOf(obj) == 'list':
            return [func(i) for i in obj]
        elif typeOf(obj) == 'tuple':
            return (func(i) for i in obj)
        elif typeOf(obj) == 'set':
            return {func(i) for i in obj}
        elif typeOf(obj) == 'str':
            return ''.join([func(i) for i in obj])
    else:
        raise BlockError(f"colApplyF only accepts one of {', '.join([i for i in BUILTIN_COLLECTIONS])}.")

@builtin
def colContains(obj, item):
    if typeOf(obj) in BUILTIN_COLLECTIONS: return item in obj
    else: raise BlockError(f"colContains: obj type should be one of {', '.join([i for i in BUILTIN_COLLECTIONS])}.")

@builtin
def colJoin(obj, joiner=''): return joiner.join(obj)

@builtin
def colIndexOf(obj, item, start=0, stop=None):
    valid_types = [i for i in BUILTIN_COLLECTIONS if i not in ('map', 'set')]
    if typeOf(obj) in valid_types:
        try:
            if stop is None: return obj.index(item, start)
            else: return obj.index(item, start, stop)
        except ValueError: raise BlockError("colIndexOf: item not found.")
    else:
        raise BlockError(f"colIndexOf only accepts one of {', '.join(valid_types)}.")

# Basic utilities
@builtin
def ask(prompt: str, forward=toStr):
    if typeOf(forward) != 'func': raise BlockError("ask: The `forward` parameter must be of type 'func'.")
    inp = input(prompt)
    return forward(inp)

@builtin
def ucp(obj): return ord(obj)
@builtin
def char(obj): return chr(obj)

# File io
@builtin
def fOpen(path, mode, *args): return open(path, mode, *args)
@builtin
def fRead(f):
    if f.readable(): return f.read()
    else: raise BlockError("Cannot read the file because it is not opened in reading mode.")
@builtin
def fWrite(f, content:str = ''):
    if f.writable(): return f.write(content)
    else: raise BlockError("Cannot write in the file because it is not opened in writing mode.")
@builtin
def fClose(f): return f.close()

# Asynchoronous
import asyncio
@builtin
def aSleep(seconds):
    async def _s(s):
        await asyncio.sleep(float(s))
        return NONE
    return _s(seconds)

@builtin
def aRun(coro):
    if not callable(coro):
        try: loop = asyncio.get_event_loop()
        except RuntimeError: loop = None
        if loop and loop.is_running():
            task = loop.create_task(coro)
            return task
        else: return asyncio.run(coro)
    else:
        try:
            result = coro()
            return aRun(result)
        except Exception as e: raise BlockError(f"aRun: {e}")

@builtin
def aCreateTask(coro):
    try: loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running(): return loop.create_task(coro)
    else:
        task = loop.create_task(coro)
        loop.run_until_complete(asyncio.sleep(0))
        return task

@builtin
def aIsCoroutine(obj): return boolean(asyncio.iscoroutine(obj) or asyncio.iscoroutinefunction(obj))
