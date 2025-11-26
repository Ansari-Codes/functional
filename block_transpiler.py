import re
import sys
from typing import List, Union


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


class EOL(ASTNode):
    """End of line marker"""
    def __init__(self):
        self.value = '\n'
        self.py_value = '\n'


def sourceToLine(source: str) -> List[str]:
    """
    Convert Block source code into a list of lines.
    - Handles multiline strings by converting them to single-line with \\n
    - Removes comments (>>, #, ///, /* */)
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
                for comment_start in ['>>', '#', '///', '/*', '*/']:
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
        for comment_start in ['>>', '#', '///', '/*', '*/']:
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


def astToPy(ast_nodes: List[ASTNode]) -> str:
    """
    Convert AST nodes to Python source code.
    Uses the .py_value of each node to generate output.
    """
    defined_functions = set()
    collection_variables = set()
    
    for idx, node in enumerate(ast_nodes):
        if isinstance(node, KEYWORD) and node.value == 'fn':
            if idx + 1 < len(ast_nodes) and isinstance(ast_nodes[idx + 1], OPERAND):
                defined_functions.add(ast_nodes[idx + 1].value)
        
        if isinstance(node, OPERAND) and node.value not in ['[', ']', ',', ':', '=']:
            if idx + 1 < len(ast_nodes) and isinstance(ast_nodes[idx + 1], OPERATOR) and ast_nodes[idx + 1].value == '=':
                if idx + 2 < len(ast_nodes):
                    next_token = ast_nodes[idx + 2]
                    if isinstance(next_token, OPERAND) and next_token.value == '[':
                        j = idx + 3
                        has_colon = False
                        while j < len(ast_nodes):
                            if isinstance(ast_nodes[j], EOL):
                                break
                            if isinstance(ast_nodes[j], OPERAND) and ast_nodes[j].value == ']':
                                break
                            if isinstance(ast_nodes[j], OPERAND) and ast_nodes[j].value == ':':
                                has_colon = True
                            j += 1
                        if not has_colon:
                            collection_variables.add(node.value)
                    elif isinstance(next_token, OPERATOR) and next_token.value == '(':
                        collection_variables.add(node.value)
                    elif isinstance(next_token, OPERATOR) and next_token.value == '{':
                        collection_variables.add(node.value)
    
    python_code = []
    current_line = ""
    i = 0
    
    while i < len(ast_nodes):
        node = ast_nodes[i]
        
        if isinstance(node, EOL):
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
                    current_line += ast_nodes[i].py_value
                    i += 1
                
                if i < len(ast_nodes) and isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == '[':
                    current_line += '('
                    i += 1
                    
                    while i < len(ast_nodes) and not (isinstance(ast_nodes[i], OPERAND) and ast_nodes[i].value == ']'):
                        if isinstance(ast_nodes[i], EOL):
                            break
                        if isinstance(ast_nodes[i], OPERATOR) and ast_nodes[i].value == '=':
                            current_line += '='
                        else:
                            current_line += ast_nodes[i].py_value
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
                    
                    current_line += ast_nodes[i].py_value
                    i += 1
                
                continue
            
            else:
                current_line += node.py_value + ' '
                i += 1
                continue
        
        if isinstance(node, OPERAND):
            if node.value == ':':
                current_line += ':'
            elif node.value == '[':
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
                
                if colon_count > 0 and comma_count >= colon_count - 1:
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
                    if has_colon_pair:
                        current_line += '{'
                    else:
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
    Converts Block source code to Python.
    """
    try:
        lines = sourceToLine(source)
        ast_nodes = linesToAst(lines)
        python_code = astToPy(ast_nodes)
        return python_code
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
