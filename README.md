
# ✅ **BLOCK LANGUAGE SYNTAX**
> It is a functional language with no methods even on builtin objects and doesn't provide OOP.
---

## **1. Strings**

* Always use **double quotes `"..."`**
* Strings can be **multiline**, but still use double quotes
* `sourceToLine()` must convert multiline strings into **a single line** using `\n`

Example:

```
"hello"
"line1
line2
line3"
```

---

## **2. Numbers**

* There is only **one numeric type**
* Any number literal is treated the same (int, float, etc.)

Examples:

```
12
3.14
-50
```

---

## **3. Conditionals**

```
if condition:
    ...
elif condition:
    ...
else:
    ...
```

---

## **4. Loops**

### **For loop**

```
for i in 1..5:
    ...
```

Meaning: inclusive range. It can also use iterable.

### **While loop**

```
while condition:
    ...
```

---

## **5. Functions**

* Declared with `fn`
* Parameters written in **square brackets**
* Uses `->` for return

Example:

```
fn add[x, y=2]:
    z = x + y
    -> z
z = add(1)
```

Where:

* `fn` → function declaration
* Return value must be after `->`

---

## **6. Operators**

* `OPERATOR` node will operate on operands to generate `.py_value`
* Operators behave the same as Python operators (`+`, `-`, `*`, `/`, `%`, `==`, etc.)
* Currect operators:
```
+, -, /, //, *, ^(pow), %,
!(not), &(and), |(or), (, ),
=, ==, !=, >=, <=, >, <
```

---

## **7. Keywords**

* `KEYWORD` node will be responsible to generate `.py_value`
* Currect keywords:
```
for, while, if, elif, else, in, -> (technically, a keyword, as it marks the return value of function)
```

---

## **8. Data Structures**

* list:
```
l = [item1, item2, item3, ...]
item = l[0]
# slicing
portion = l[0,1] 
l[0] = itemx
```

* tuple:
```
t = (item1, item2, item3, ...)
item = t[0]
# slicing
portion = t[0,1]
```

* set:
```
s = {item1, item2, item3, ...}
```

* dict:
```
d = ['key':value, 'key':value2, ...]
```
---

## **9. Comments**

A line is a **comment ONLY if it starts the line** (no leading spaces).

Valid comment starters:

```
>>
#
///
/*
*/
```

* `/* ... */` creates a block comment region
* Comments are removed by `sourceToLine()`

---
---

## ✅ **BLOCK TARNSPILATION METHODLOGY**

### **1. There will be only *three* main functions:**

1. `sourceToLine()`

   * Converts the entire source code into a list of lines.
   * Multiline strings must be turned into **single-line string literals** using `\n`.
   * Comments must be removed.
   * All other text preserved line-by-line.

2. `linesToAst()`

   * Takes the list of lines created by `sourceToLine()`.
   * Converts each line into a list of AST nodes.
   * Uses an `EOL()` class at end of each line.

3. `astToPy()`

   * Takes all AST nodes from `linesToAst()`.
   * Outputs Python code as text (strings).
   * Uses `.py_value` of each node.

---

## ✅ **2. AST classes**

Each AST class has:

* `.value` → raw/original value from source
* `.py_value` → Python-ready version of the value

The classes you defined:

### **STRING**

* `.value` = raw string
* `.py_value` = automatically generated valid Python string

### **NUMBER**

* Only one number type in block language.

### **OPERATOR**

* Has `.value` and `.py_value`
* Uses one or more OPERANDs
* Produces python expression
* Also has operator_map for simple block <-> python mapping
* special_operators is just a list like '..' which is to be handled correctly
* Its method will create its .py_value

### **OPERAND**

* A node representing any literal or variable the operator uses.

### **SPACE**

* Represents indentation at beginning of line
* Calculates number of spaces (indentation level)
* Always before a line

---

## ✅ **3. Comments**

Comments are only considered comments **if they start at the beginning of the line**.

Valid comment beginnings:

```
>>
# 
// 
/*
mutline
*/
= ...
```

also:

* `/* ... */` should be treated as block comment (ignore everything inside)
* All comments are removed by `sourceToLine()`.

---

## ✅ **4. Custom Error Class**

You want a custom error:

```
BlockError
```

that the transpiler will use.

---

## ✅ **5. The name of the language**

Language will be called **block**.

