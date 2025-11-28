class BlockError(Exception):
    """Custom exception for Block language transpilation errors"""
    pass

BUILTIN_TYPES = ("str", "num", "boolean", "list", "tuple", "set", "map", "func", "none")
BUILTIN_FUNCTIONS = ("echo", "typeOf", "toStr", "toNum")
BUILTIN_CONSTANTS = {        
        'true': ('boolean', 'boolean(True)'),
        'false': ('boolean', 'boolean()'),
        'none': ('str', 'none'),
    }

class boolean(int):
    def __init__(self, value=False) -> None:
        self.value = bool(value)
    
    def __repr__(self) -> str:
        return self.value.__str__().lower()

    def __str__(self) -> str:
        return self.__repr__()
class none: None #type:ignore

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

def toStr(obj): return f"{obj!r}"
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


block_x=1
block_y=-2
block_strings="hello"
block_multi="line1\nline2\nline3"
if block_x>0:
    echo("X is positive")
elif block_x<0:
    echo("X is negative")
else:
    echo("X is zero")
while block_x<11:
    echo(block_x)
    block_x=block_x+1
for block_i in range(1, 2 + 1):
    echo(block_i)
def block_add(block_x,block_y=2):
    return block_x+block_y
block_z=block_add(1)
block_lst=[0,1,2,3]
block_first=block_lst[0]
block_slc=block_lst[0:2+1]
echo(block_first,block_slc)
block_dct={0:1,1:2,2:3}
echo(typeOf(block_dct))
echo(block_slc)
echo(block_first)
echo(block_z)
echo(typeOf(block_add))
block_x="10"
echo(typeOf(toNum(block_x)))
echo(boolean(True))