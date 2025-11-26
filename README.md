# Block Language Transpiler

## Overview
A Python-based transpiler that converts Block language source code to executable Python code. Block is a custom programming language with simplified syntax that transpiles to Python.

## Project Structure
- `block_transpiler.py` - Main transpiler implementation with AST classes and conversion functions
- `examples/` - Example Block language files demonstrating syntax features

## Block Language Features
- **Strings**: Double-quoted, support multiline
- **Numbers**: Single numeric type (int/float)
- **Conditionals**: `if`, `elif`, `else`
- **Loops**: `for i in 1..5:` (inclusive range), `while`
- **Functions**: `fn name[params]:` with `->` for return
- **Operators**: Standard operators with `^` for power, `!` for not, `&` for and, `|` for or
- **Comments**: `>>`, `#`, `///`, `/* */` (must start at line beginning)

## Transpilation Pipeline
1. `sourceToLine()` - Parse source, handle multiline strings, remove comments
2. `linesToAst()` - Convert lines to AST nodes
3. `astToPy()` - Generate Python code from AST

## Usage
```bash
# Transpile a .block file
python block_transpiler.py input.block output.py

# Transpile inline code
python block_transpiler.py -c 'x = 5'
```

## Recent Changes
- 2025-11-26: Initial implementation with full Block language support
now; we have to add:
dict
list
set
tuple
and indexing, slicing and this like others
syntax:
list = [item1, item2, item3, ...]
list[0]
list[0,1] # means list items from 0 to 1
list[] # means list[:], to copy
tuple = (item1, item2, item3, ...)
we cannot assign items, indexing, slicing and copying is same as list
set = {item1, item2, item3, ...}
no slicing, indexing for a set
dict = ['key': value, 'key2':value2, ...]

keys should be distinct, if duplicated, last key value pair is persisted
accessing:
No method calls, no this like else!
because block is a functional level, there are no methods here
no oop
so, you have not to add method handling
just create syntax handling!

