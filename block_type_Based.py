import re
import sys
from typing import List, Union, Dict, Set, Optional


class BlockError(Exception):
    """Custom exception for Block language transpilation errors"""
    pass


class ASTNode:
    """Base class for all AST nodes"""
    def __init__(self, value):
        self.value = value
        self.py_value = value
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"


class STRING(ASTNode):
    """String literal node"""
    def __init__(self, value):
        self.value = value
        self.py_value = f'"{value}"'


class NUMBER(ASTNode):
    """Numeric literal node"""
    def __init__(self, value):
        self.value = value
        self.py_value = str(value)


class OPERAND(ASTNode):
    """Operand node (variable name, literal, or expression)"""
    def __init__(self, value):
        self.value = value
        self.py_value = str(value)


class OPERATOR(ASTNode):
    """Operator node with Block to Python mapping"""
    
    operator_map = {
        '^': '**',
        '!': 'not ',
        '&': ' and ',
        '|': ' or ',
        '+': '+',
        '-': '-',
        '*': '*',
        '/': '/',
        '//': '//',
        '%': '%',
        '=': '=',
        '==': '==',
        '!=': '!=',
        '>=': '>=',
        '<=': '<=',
        '>': '>',
        '<': '<',
        '(': '(',
        ')': ')',
    }
    
    special_operators = ['..']
    
    def __init__(self, value):
        self.value = value
        if value in self.operator_map:
            self.py_value = self.operator_map[value]
        elif value == '..':
            self.py_value = '..'
        else:
            self.py_value = value


class KEYWORD(ASTNode):
    """Keyword node"""
    
    keywords = ['for', 'while', 'if', 'elif', 'else', 'in', 'fn', '->']
    
    def __init__(self, value):
        self.value = value
        if value == '->':
            self.py_value = 'return'
        elif value == 'fn':
            self.py_value = 'def'
        else:
            self.py_value = value


class SPACE(ASTNode):
    """Indentation node"""
    def __init__(self, value):
        self.value = value
        self.py_value = value
    
    def get_indent_level(self):
        """Calculate indentation level"""
        return len(self.value)


class TYPE(ASTNode):
    """Type annotation node (stripped in transpilation)"""
    def __init__(self, value):
        self.value = value
        self.py_value = ''  # Type annotations don't appear in Python output


class EOL(ASTNode):
    """End of line marker"""
    def __init__(self):
        self.value = '\n'
        self.py_value = '\n'


class TypeSystem:
    """Track types of variables and functions in Block code"""
    
    BUILTIN_TYPES = {'num', 'bool', 'str', 'func', 'list', 'tuple', 'map', 'set'}
    BUILTIN_FUNCTIONS = {'print', 'len', 'range', 'type', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple'}
    BUILTIN_CONSTANTS = {
        'true': ('bool', 'True'),
        'false': ('bool', 'False'),
        'none': ('str', 'None'),  # None type in Python
    }
    
    def __init__(self):
        self.variables: Dict[str, str] = {}  # var_name -> type
        self.functions: Dict[str, str] = {}  # func_name -> return_type
        self.function_params: Dict[str, List[tuple]] = {}  # func_name -> [(param_name, param_type), ...]
        # Initialize builtin functions
        for fname in self.BUILTIN_FUNCTIONS:
            self.functions[fname] = 'num'  # default return type
    
    def define_variable(self, name: str, var_type: str) -> None:
        """Define a variable with its type"""
        if var_type not in self.BUILTIN_TYPES and not self._is_collection_type(var_type):
            raise BlockError(f"Undefined type '{var_type}'")
        self.variables[name] = var_type
    
    def define_function(self, name: str, return_type: str, params: List[tuple]) -> None:
        """Define a function with return type and parameters"""
        if return_type not in self.BUILTIN_TYPES and not self._is_collection_type(return_type):
            raise BlockError(f"Undefined return type '{return_type}'")
        self.functions[name] = return_type
        self.function_params[name] = params
        for param_name, param_type in params:
            if param_type not in self.BUILTIN_TYPES and not self._is_collection_type(param_type):
                raise BlockError(f"Undefined parameter type '{param_type}'")
    
    def is_defined_variable(self, name: str) -> bool:
        """Check if variable is defined"""
        return name in self.variables
    
    def is_defined_function(self, name: str) -> bool:
        """Check if function is defined"""
        return name in self.functions
    
    def get_variable_type(self, name: str) -> Optional[str]:
        """Get variable type"""
        return self.variables.get(name)
    
    def get_function_type(self, name: str) -> Optional[str]:
        """Get function return type"""
        return self.functions.get(name)
    
    def _is_collection_type(self, type_str: str) -> bool:
        """Check if type is a valid collection type"""
        # [type], (type), {type}, {key:val}
        if not type_str:
            return False
        if type_str.startswith('[') and type_str.endswith(']'):
            return True
        if type_str.startswith('(') and type_str.endswith(')'):
            return True
        if type_str.startswith('{') and type_str.endswith('}'):
            return True
        return False


def sourceToLine(source: str) -> List[str]:
    """
    Convert Block source code into a list of lines.
    - Handles multiline strings by converting them to single-line with \\n
    - Removes comments (>>, #, //, /* */)
    - Preserves all other text line-by-line
    """
    lines = []
    i = 0
    in_block_comment = False
    current_line = ""
    in_string = False
    string_start = -1
    
    while i < len(source):
        char = source[i]
        
        if in_block_comment:
            if i + 1 < len(source) and source[i:i+2] == '*/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        
        if char == '"' and (i == 0 or source[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_start = i
            else:
                string_content = source[string_start+1:i]
                string_content = string_content.replace('\n', '\\n').replace('\r', '\\r')
                current_line += '"' + string_content + '"'
                in_string = False
                string_start = -1
            i += 1
            continue
        
        if in_string:
            i += 1
            continue
        
        if char == '\n':
            line = current_line.strip()
            
            if line:
                is_comment = False
                for comment_start in ['>>', '#', '//', '/*', '*/']:
                    if line.startswith(comment_start):
                        is_comment = True
                        break
                
                if line.startswith('/*'):
                    in_block_comment = True
                    is_comment = True
                
                if not is_comment:
                    lines.append(current_line.rstrip())
            
            current_line = ""
            i += 1
            continue
        
        current_line += char
        i += 1
    
    if current_line.strip():
        line = current_line.strip()
        is_comment = False
        for comment_start in ['>>', '#', '//', '/*', '*/']:
            if line.startswith(comment_start):
                is_comment = True
                break
        
        if not is_comment:
            lines.append(current_line.rstrip())
    
    return lines


def linesToAst(lines: List[str]) -> List[ASTNode]:
    """
    Convert lines of Block code into AST nodes.
    Each line is tokenized and converted to appropriate AST nodes.
    """
    ast_nodes = []
    
    for line in lines:
        if not line:
            ast_nodes.append(EOL())
            continue
        
        indent = len(line) - len(line.lstrip())
        if indent > 0:
            ast_nodes.append(SPACE(' ' * indent))
        
        content = line.lstrip()
        tokens = tokenize_line(content)
        
        for token in tokens:
            ast_nodes.append(token)
        
        ast_nodes.append(EOL())
    
    return ast_nodes


def tokenize_line(content: str) -> List[ASTNode]:
    """Tokenize a single line of Block code into AST nodes"""
    tokens = []
    i = 0
    
    while i < len(content):
        if content[i].isspace():
            i += 1
            continue
        
        if content[i] == '"':
            end = i + 1
            while end < len(content):
                if content[end] == '"' and content[end-1] != '\\':
                    break
                end += 1
            string_content = content[i+1:end]
            tokens.append(STRING(string_content))
            i = end + 1
            continue
        
        if content[i].isdigit() or (content[i] == '-' and i+1 < len(content) and content[i+1].isdigit()):
            end = i + 1
            has_dot = False
            while end < len(content) and (content[end].isdigit() or (content[end] == '.' and not has_dot)):
                if content[end] == '.':
                    if end + 1 < len(content) and content[end+1] == '.':
                        break
                    has_dot = True
                end += 1
            num_str = content[i:end]
            if '.' in num_str:
                tokens.append(NUMBER(float(num_str)))
            else:
                tokens.append(NUMBER(int(num_str)))
            i = end
            continue
        
        if i + 1 < len(content) and content[i:i+2] in ['..', '==', '!=', '>=', '<=', '//', '->']:
            op = content[i:i+2]
            if op == '->':
                tokens.append(KEYWORD('->'))
            else:
                tokens.append(OPERATOR(op))
            i += 2
            continue
        
        if content[i] in '+-*/^%=!&|()<>{}':
            tokens.append(OPERATOR(content[i]))
            i += 1
            continue
        
        if content[i] == '[' or content[i] == ']' or content[i] == ',' or content[i] == ':':
            tokens.append(OPERAND(content[i]))
            i += 1
            continue
        
        if content[i].isalpha() or content[i] == '_':
            end = i + 1
            while end < len(content) and (content[end].isalnum() or content[end] == '_'):
                end += 1
            word = content[i:end]
            
            if word in KEYWORD.keywords:
                tokens.append(KEYWORD(word))
            else:
                tokens.append(OPERAND(word))
            i = end
            continue
        
        i += 1
    
    return tokens


def extract_type_info(ast_nodes: List[ASTNode], start_idx: int) -> tuple:
    """Extract type name from colon position, returns (type_name, end_idx)"""
    if start_idx >= len(ast_nodes) or not (isinstance(ast_nodes[start_idx], OPERAND) and ast_nodes[start_idx].value == ':'):
        return None, start_idx
    
    idx = start_idx + 1
    type_tokens = []
    
    while idx < len(ast_nodes):
        node = ast_nodes[idx]
        if isinstance(node, EOL) or (isinstance(node, OPERAND) and node.value in ['=', ',']):
            break
        if isinstance(node, OPERAND) and node.value.isalpha():
            type_tokens.append(node.value)
            idx += 1
        elif isinstance(node, OPERAND) and node.value in ['[', '(', '{']:
            type_tokens.append(node.value)
            bracket = node.value
            close_bracket = {'[': ']', '(': ')', '{': '}'}[bracket]
            idx += 1
            depth = 1
            while idx < len(ast_nodes) and depth > 0:
                if isinstance(ast_nodes[idx], OPERAND):
                    if ast_nodes[idx].value == bracket:
                        depth += 1
                    elif ast_nodes[idx].value == close_bracket:
                        depth -= 1
                    type_tokens.append(ast_nodes[idx].value)
                idx += 1
            break
        else:
            break
    
    type_name = ''.join(type_tokens) if type_tokens else None
    return type_name, idx


def infer_value_type(ast_nodes: List[ASTNode], start_idx: int, type_system: TypeSystem) -> str:
    """Infer the type of a value starting at start_idx"""
    if start_idx >= len(ast_nodes):
        return 'num'  # default
    
    node = ast_nodes[start_idx]
    
    # Check for builtin constants
    if isinstance(node, OPERAND) and node.value in TypeSystem.BUILTIN_CONSTANTS:
        const_type, _ = TypeSystem.BUILTIN_CONSTANTS[node.value]
        return const_type
    
    if isinstance(node, STRING):
        return 'str'
    if isinstance(node, NUMBER):
        return 'num'
    if isinstance(node, OPERAND):
        if node.value == '[':
            return 'list'
        if node.value == '(':
            return 'tuple'
        if node.value == '{':
            return 'set'  # or map, need more context
        if node.value in type_system.variables:
            return type_system.variables[node.value]
        if node.value in type_system.functions:
            return 'func'
    
    return 'num'  # default


def astToPy(ast_nodes: List[ASTNode]) -> str:
    """
    Convert AST nodes to Python source code with type checking and identifier validation.
    Uses the .py_value of each node to generate output.
    """
    type_system = TypeSystem()
    collection_variables = set()
    
    # First pass: collect function and variable definitions
    i = 0
    while i < len(ast_nodes):
        node = ast_nodes[i]
        
        # Collect loop variable definitions (for i in ...)
        if isinstance(node, KEYWORD) and node.value == 'for':
            j = i + 1
            if j < len(ast_nodes) and isinstance(ast_nodes[j], OPERAND):
                loop_var = ast_nodes[j].value
                # Register as num type (default for loop variables)
                try:
                    type_system.define_variable(loop_var, 'num')
                except BlockError as e:
                    raise e
        
        # Collect function definitions
        if isinstance(node, KEYWORD) and node.value == 'fn':
            if i + 1 < len(ast_nodes) and isinstance(ast_nodes[i + 1], OPERAND):
                func_name = ast_nodes[i + 1].value
                # Find return type
                j = i + 2
                while j < len(ast_nodes) and not (isinstance(ast_nodes[j], OPERAND) and ast_nodes[j].value == ']'):
                    j += 1
                j += 1  # skip ]
                ret_type = 'num'
                if j < len(ast_nodes) and isinstance(ast_nodes[j], OPERAND) and ast_nodes[j].value == ':':
                    ret_type_name, _ = extract_type_info(ast_nodes, j)
                    if ret_type_name in TypeSystem.BUILTIN_TYPES:
                        ret_type = ret_type_name
                
                # Extract parameters (with optional default values)
                params = []
                param_defaults = {}  # param_name -> default_value
                k = i + 2
                if k < len(ast_nodes) and isinstance(ast_nodes[k], OPERAND) and ast_nodes[k].value == '[':
                    k += 1
                    while k < len(ast_nodes) and not (isinstance(ast_nodes[k], OPERAND) and ast_nodes[k].value == ']'):
                        if isinstance(ast_nodes[k], OPERAND) and ast_nodes[k].value not in [',', ':']:
                            param_name = ast_nodes[k].value
                            param_type = 'num'
                            k += 1
                            
                            # Skip type annotation if present
                            if k < len(ast_nodes) and isinstance(ast_nodes[k], OPERAND) and ast_nodes[k].value == ':':
                                pt, type_end = extract_type_info(ast_nodes, k)
                                if pt in TypeSystem.BUILTIN_TYPES:
                                    param_type = pt
                                k = type_end
                            
                            # Check for default value (param_name=value)
                            if k < len(ast_nodes) and isinstance(ast_nodes[k], OPERATOR) and ast_nodes[k].value == '=':
                                k += 1
                                # Collect default value tokens until comma or closing bracket
                                default_tokens = []
                                while k < len(ast_nodes) and not (isinstance(ast_nodes[k], OPERAND) and ast_nodes[k].value in [',', ']']):
                                    default_tokens.append(ast_nodes[k])
                                    k += 1
                                default_value = ''.join(t.py_value if hasattr(t, 'py_value') else str(t) for t in default_tokens).strip()
                                param_defaults[param_name] = default_value
                            
                            params.append((param_name, param_type))
                            continue
                        k += 1
                
                try:
                    type_system.define_function(func_name, ret_type, params)
                except BlockError as e:
                    raise e
        
        # Collect variable definitions (with or without types)
        if isinstance(node, OPERAND) and node.value not in ['[', ']', ',', ':', '=']:
            if i + 1 < len(ast_nodes):
                next_node = ast_nodes[i + 1]
                var_name = node.value
                
                # Case 1: Type annotation (x:num = value)
                if isinstance(next_node, OPERAND) and next_node.value == ':':
                    var_type, type_end = extract_type_info(ast_nodes, i + 1)
                    if var_type:
                        if var_type in TypeSystem.BUILTIN_TYPES or type_system._is_collection_type(var_type):
                            try:
                                type_system.define_variable(var_name, var_type)
                            except BlockError as e:
                                raise e
                    
                    # Check if it's an assignment
                    if type_end < len(ast_nodes) and isinstance(ast_nodes[type_end], OPERATOR) and ast_nodes[type_end].value == '=':
                        next_token = ast_nodes[type_end + 1] if type_end + 1 < len(ast_nodes) else None
                        if isinstance(next_token, OPERAND) and next_token.value in ['[', '(', '{']:
                            collection_variables.add(var_name)
                
                # Case 2: No type annotation (x = value)
                elif isinstance(next_node, OPERATOR) and next_node.value == '=':
                    # Infer type from the value
                    value_idx = i + 2
                    if value_idx < len(ast_nodes):
                        value_node = ast_nodes[value_idx]
                        inferred_type = infer_value_type(ast_nodes, value_idx, type_system)
                        try:
                            type_system.define_variable(var_name, inferred_type)
                        except BlockError as e:
                            raise e
                        
                        # Track if it's a collection
                        if isinstance(value_node, OPERAND) and value_node.value in ['[', '(', '{']:
                            collection_variables.add(var_name)
        
        i += 1
    
    # Second pass: generate Python code with validation
    python_code = []
    current_line = ""
    i = 0
    
    in_control_flow = False
    
    while i < len(ast_nodes):
        node = ast_nodes[i]
        
        if isinstance(node, EOL):
            # Add colon for control flow and function def statements
            if current_line and not current_line.rstrip().endswith(':'):
                if any(current_line.strip().startswith(kw) for kw in ['if ', 'elif ', 'while ', 'else', 'def ']):
                    current_line += ':'
            python_code.append(current_line)
            current_line = ""
            i += 1
            continue
        
        if isinstance(node, SPACE):
            current_line += node.py_value
            i += 1
            continue
        
        if isinstance(node, KEYWORD):
            if node.value == 'fn':
                current_line += 'def '
                i += 1
                
                if i < len(ast_nodes) and isinstance(ast_nodes[i], OPERAND):
                    func_name = ast_nodes[i].value
                    current_line += f'block_{func_name}'
                    i += 1
                
                if i < len(ast_nodes) and isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == '[':
                    current_line += '('
                    i += 1
                    
                    while i < len(ast_nodes) and not (isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ']'):
                        if isinstance(ast_nodes[i], EOL):
                            break
                        if isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ':':
                            # Skip type annotation (colon and type)
                            type_name, type_end = extract_type_info(ast_nodes, i)
                            i = type_end
                            continue
                        elif isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value.isalpha() and ast_nodes[i].value not in [',']:
                            param_name = ast_nodes[i].value
                            current_line += f'block_{param_name}'
                            i += 1
                            
                            # Check for default value (=)
                            if i < len(ast_nodes) and isinstance(ast_nodes[i], OPERATOR) and ast_nodes[i].value == '=':
                                current_line += '='
                                i += 1
                                # Collect default value tokens
                                while i < len(ast_nodes) and not (isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value in [',', ']']):
                                    if isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ':':
                                        # Skip type after default value
                                        type_name, type_end = extract_type_info(ast_nodes, i)
                                        i = type_end
                                        continue
                                    current_line += ast_nodes[i].py_value
                                    i += 1
                            continue
                        elif isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ',':
                            current_line += ','
                        i += 1
                    
                    if i < len(ast_nodes) and isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ']':
                        current_line += ')'
                        i += 1
                
                continue
            
            elif node.value == '->':
                current_line += 'return '
                i += 1
                continue
            
            elif node.value == 'for':
                current_line += 'for '
                i += 1
                
                while i < len(ast_nodes):
                    if isinstance(ast_nodes[i], EOL):
                        break
                    
                    if isinstance(ast_nodes[i], KEYWORD) and ast_nodes[i].value == 'in':
                        current_line += ' in '
                        i += 1
                        
                        iterable_tokens = []
                        while i < len(ast_nodes):
                            if isinstance(ast_nodes[i], EOL):
                                break
                            if isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ':':
                                break
                            iterable_tokens.append(ast_nodes[i])
                            i += 1
                        
                        has_range_operator = any(isinstance(t, OPERATOR) and t.value == '..' for t in iterable_tokens)
                        
                        if has_range_operator:
                            range_start_tokens = []
                            range_end_tokens = []
                            found_range_op = False
                            
                            for token in iterable_tokens:
                                if isinstance(token, OPERATOR) and token.value == '..':
                                    found_range_op = True
                                elif not found_range_op:
                                    range_start_tokens.append(token)
                                else:
                                    range_end_tokens.append(token)
                            
                            start_expr = ''.join(t.py_value if hasattr(t, 'py_value') else str(t) for t in range_start_tokens)
                            end_expr = ''.join(t.py_value if hasattr(t, 'py_value') else str(t) for t in range_end_tokens)
                            
                            if start_expr and end_expr:
                                current_line += f'range({start_expr}, {end_expr} + 1)'
                            else:
                                current_line += ''.join(t.py_value if hasattr(t, 'py_value') else str(t) for t in iterable_tokens)
                        else:
                            current_line += ''.join(t.py_value if hasattr(t, 'py_value') else str(t) for t in iterable_tokens)
                        
                        continue
                    
                    if isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value.isalpha():
                        current_line += f'block_{ast_nodes[i].value}'
                    else:
                        current_line += ast_nodes[i].py_value
                    i += 1
                
                continue
            
            else:
                # Handle other keywords (if, elif, else, while)
                if node.value in ['if', 'elif', 'while']:
                    current_line += node.value + ' '
                elif node.value == 'else':
                    current_line += node.value
                else:
                    current_line += node.py_value + ' '
                i += 1
                continue
        
        if isinstance(node, TYPE):
            i += 1
            continue
        
        if isinstance(node, OPERAND):
            if node.value == ':':
                # Only skip colons for type annotations (when preceded by variable name/closing bracket)
                # Keep colons for dict literals
                if i > 0:
                    prev = ast_nodes[i-1]
                    # Check if this looks like a type annotation (id: type)
                    is_type_annotation = (isinstance(prev, OPERAND) and (prev.value.isalpha() or prev.value == ']'))
                    if is_type_annotation and i - 2 >= 0:
                        # Additional check: see if this is followed by a known type
                        if i + 1 < len(ast_nodes):
                            next_node = ast_nodes[i + 1]
                            if isinstance(next_node, TYPE) or (isinstance(next_node, OPERAND) and next_node.value in TypeSystem.BUILTIN_TYPES):
                                type_name, type_end = extract_type_info(ast_nodes, i)
                                i = type_end
                                continue
                # Output the colon (for dict literals)
                current_line += ':'
                i += 1
                continue
            elif node.value == '[':
                # Handle bracket access/literals
                bracket_content = []
                j = i + 1
                bracket_depth = 1
                while j < len(ast_nodes) and bracket_depth > 0:
                    if isinstance(ast_nodes[j], EOL):
                        break
                    if isinstance(ast_nodes[j], OPERAND):
                        if ast_nodes[j].value == '[':
                            bracket_depth += 1
                        elif ast_nodes[j].value == ']':
                            bracket_depth -= 1
                            if bracket_depth == 0:
                                break
                    bracket_content.append(ast_nodes[j])
                    j += 1
                
                prev_var_name = None
                is_after_var = i > 0 and isinstance(ast_nodes[i-1], OPERAND) and ast_nodes[i-1].value not in ['[', ']', ',', ':', '=']
                if is_after_var:
                    prev_var_name = ast_nodes[i-1].value
                
                is_collection = prev_var_name in collection_variables if prev_var_name else False
                
                has_colon_pair = False
                has_comma = False
                is_empty = len(bracket_content) == 0
                colon_count = 0
                comma_count = 0
                
                for tok in bracket_content:
                    if isinstance(tok, OPERAND):
                        if tok.value == ':':
                            colon_count += 1
                        elif tok.value == ',':
                            comma_count += 1
                
                # If ANY token contains a colon, it's a dict
                if colon_count > 0:
                    has_colon_pair = True
                if comma_count > 0:
                    has_comma = True
                
                if is_after_var and is_collection:
                    if is_empty:
                        current_line += '[:]'
                        i = j + 1
                        continue
                    elif has_comma and not has_colon_pair:
                        slice_parts = []
                        current_part = []
                        for tok in bracket_content:
                            if isinstance(tok, OPERAND) and tok.value == ',':
                                slice_parts.append(current_part)
                                current_part = []
                            else:
                                current_part.append(tok)
                        if current_part:
                            slice_parts.append(current_part)
                        
                        if len(slice_parts) == 2:
                            start_expr = ''.join(t.py_value for t in slice_parts[0])
                            end_expr = ''.join(t.py_value for t in slice_parts[1])
                            current_line += f'[{start_expr}:{end_expr}+1]'
                            i = j + 1
                            continue
                        else:
                            current_line += '['
                    else:
                        current_line += '['
                elif is_after_var:
                    current_line += '('
                else:
                    # Standalone bracket (not after variable)
                    if has_colon_pair:
                        # Has colons = dict
                        current_line += '{'
                    else:
                        # No colons = list (will validate for unhashable types)
                        # Check if list contains unhashable types (dicts)
                        has_dict = False
                        depth = 0
                        for idx, tok in enumerate(bracket_content):
                            if isinstance(tok, OPERAND) and tok.value == '[':
                                depth += 1
                                # Check if next tokens have a colon (dict inside)
                                for inner_idx in range(idx + 1, len(bracket_content)):
                                    inner = bracket_content[inner_idx]
                                    if isinstance(inner, OPERAND) and inner.value == ']':
                                        break
                                    if isinstance(inner, OPERAND) and inner.value == ':':
                                        has_dict = True
                                        break
                            elif isinstance(tok, OPERAND) and tok.value == ']':
                                depth -= 1
                        
                        if has_dict:
                            raise BlockError("Cannot use dict (unhashable) type in set/list literal")
                        current_line += '['
            elif node.value == ']':
                paren_count = 0
                bracket_count = 0
                brace_count = 0
                for c in reversed(current_line):
                    if c == ')':
                        paren_count += 1
                    elif c == '(':
                        paren_count -= 1
                        if paren_count < 0:
                            current_line += ')'
                            break
                    elif c == ']':
                        bracket_count += 1
                    elif c == '[':
                        bracket_count -= 1
                        if bracket_count < 0:
                            current_line += ']'
                            break
                    elif c == '}':
                        brace_count += 1
                    elif c == '{':
                        brace_count -= 1
                        if brace_count < 0:
                            current_line += '}'
                            break
                else:
                    if paren_count < 0:
                        current_line += ')'
                    elif brace_count < 0:
                        current_line += '}'
                    else:
                        current_line += ']'
            elif node.value.isalpha() or node.value == '_':
                # Identifier - check if defined and add block_ prefix
                if node.value not in [',']:
                    # Check if builtin constant first
                    if node.value in TypeSystem.BUILTIN_CONSTANTS:
                        _, py_value = TypeSystem.BUILTIN_CONSTANTS[node.value]
                        current_line += py_value
                    # Check if builtin function
                    elif node.value in TypeSystem.BUILTIN_FUNCTIONS:
                        current_line += node.value
                    # Check next token to see if it's a function call or variable use
                    elif i + 1 < len(ast_nodes):
                        next_token = ast_nodes[i + 1]
                        if isinstance(next_token, OPERATOR) and next_token.value == '(':
                            # Function call with ()
                            if not type_system.is_defined_function(node.value):
                                raise BlockError(f"Undefined function '{node.value}'")
                            current_line += f'block_{node.value}'
                        elif isinstance(next_token, OPERATOR) and next_token.value == '=':
                            # Variable assignment (new definition)
                            current_line += f'block_{node.value}'
                        elif isinstance(next_token, OPERAND) and next_token.value == ':':
                            # Type annotation - just output the identifier, type will be skipped
                            current_line += f'block_{node.value}'
                        else:
                            # Variable use
                            if not type_system.is_defined_variable(node.value) and not type_system.is_defined_function(node.value):
                                raise BlockError(f"Undefined identifier '{node.value}'")
                            else:
                                current_line += f'block_{node.value}'
                    else:
                        current_line += f'block_{node.value}'
            else:
                current_line += node.py_value
        else:
            current_line += node.py_value
        
        i += 1
    
    if current_line:
        python_code.append(current_line)
    
    return '\n'.join(python_code)


def transpile(source: str) -> str:
    """
    Main transpiler function.
    Converts Block source code to Python with type checking and identifier validation.
    """
    try:
        lines = sourceToLine(source)
        ast_nodes = linesToAst(lines)
        python_code = astToPy(ast_nodes)
        return python_code
    except BlockError as e:
        raise e
    except Exception as e:
        raise BlockError(f"Transpilation error: {str(e)}")


def main():
    """CLI interface for the Block transpiler"""
    if len(sys.argv) < 2:
        print("Usage: python block_transpiler.py <input.block> [output.py]")
        print("   or: python block_transpiler.py -c '<block code>'")
        sys.exit(1)
    
    if sys.argv[1] == '-c':
        if len(sys.argv) < 3:
            print("Error: -c requires code argument")
            sys.exit(1)
        
        source = sys.argv[2]
        try:
            python_code = transpile(source)
            print(python_code)
        except BlockError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.block', '.py')
        
        try:
            with open(input_file, 'r') as f:
                source = f.read()
            
            python_code = transpile(source)
            
            with open(output_file, 'w') as f:
                f.write(python_code)
            
            print(f"Successfully transpiled {input_file} -> {output_file}")
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
        except BlockError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
