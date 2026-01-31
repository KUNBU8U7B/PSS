import sys
import subprocess
import os
import re
import tempfile
import shutil

# ==========================================
# LEXER
# ==========================================

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line})"

TOKEN_TYPES = [
    ('COMMENT', r'#.*'),
    ('STRING', r'"[^"]*"'),
    ('DECIMAL', r'\b\d+\.\d+\b'),
    ('NUMBER', r'\b\d+\b'),
    ('KEYWORD', r'\b(program|end|number|decimal|string|text|bool|byte|print|if|else|repeat|times|true|false|function|return|void|new|class|extends|public|private|import|use|as|test|assert)\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OPERATOR', r'==|!=|<=|>=|->|\+|-|\*|/|%|=|<|>|:|\.|,'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('NEWLINE', r'\n'),
    ('WHITESPACE', r'[ ]+'),
]

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.line = 1
        self.indent_stack = [0]

    def tokenize(self):
        lines = self.code.split('\n')
        for i, line_text in enumerate(lines, 1):
            self.line = i
            if not line_text.strip() or line_text.strip().startswith('#'):
                continue
            
            # Handle indentation
            whitespace_match = re.match(r'^ +', line_text)
            current_indent = len(whitespace_match.group(0)) if whitespace_match else 0
            
            if current_indent > self.indent_stack[-1]:
                self.tokens.append(Token('INDENT', current_indent, self.line))
                self.indent_stack.append(current_indent)
            elif current_indent < self.indent_stack[-1]:
                while current_indent < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append(Token('DEDENT', current_indent, self.line))
                if current_indent != self.indent_stack[-1]:
                    raise SyntaxError(f"Indentation error at line {self.line}")

            self._tokenize_line(line_text.strip())
            self.tokens.append(Token('NEWLINE', '\n', self.line))

        # Close any remaining indents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token('DEDENT', 0, self.line))
            
        return self.tokens

    def _tokenize_line(self, line):
        pos = 0
        while pos < len(line):
            match = None
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(line, pos)
                if match:
                    value = match.group(0)
                    if token_type not in ('WHITESPACE', 'COMMENT'):
                        self.tokens.append(Token(token_type, value, self.line))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Illegal character '{line[pos]}' at line {self.line}")

# ==========================================
# PARSER
# ==========================================

class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class VarDeclNode(ASTNode):
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

class AssignmentNode(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, expressions):
        self.expressions = expressions

class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class RepeatNode(ASTNode):
    def __init__(self, count, body):
        self.count = count
        self.body = body

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class LiteralNode(ASTNode):
    def __init__(self, value, type):
        self.value = value
        self.type = type

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

class FunctionNode(ASTNode):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class ClassNode(ASTNode):
    def __init__(self, name, body, parent=None):
        self.name = name
        self.body = body
        self.parent = parent

class NewNode(ASTNode):
    def __init__(self, class_name, args):
        self.class_name = class_name
        self.args = args

class CallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MemberAccessNode(ASTNode):
    def __init__(self, object, member):
        self.object = object
        self.member = member

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens):
            return None
        return self.tokens[self.pos + offset]

    def consume(self, expected_type=None, expected_value=None):
        token = self.peek()
        if not token:
            raise SyntaxError(f"Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type} at line {token.line}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{token.value}' at line {token.line}")
        self.pos += 1
        return token

    def parse(self):
        self.consume('KEYWORD', 'program')
        name = self.consume('IDENTIFIER').value
        while self.peek() and self.peek().type == 'NEWLINE':
            self.consume('NEWLINE')
        
        has_indent = False
        if self.peek() and self.peek().type == 'INDENT':
            self.consume('INDENT')
            has_indent = True
            
        body = self.parse_block()
        
        if has_indent:
            self.consume('DEDENT')
            
        while self.peek() and self.peek().type == 'NEWLINE':
            self.consume('NEWLINE')
            
        self.consume('KEYWORD', 'end')
        return ProgramNode(name, body)

    def parse_block(self):
        statements = []
        while self.peek() and self.peek().value != 'end' and self.peek().type != 'DEDENT':
            while self.peek() and self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
            if not self.peek() or self.peek().value == 'end' or self.peek().type == 'DEDENT':
                break
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.peek()
        if token.type == 'KEYWORD':
            if token.value in ('number', 'decimal', 'string', 'text', 'bool', 'byte', 'void'):
                return self.parse_var_decl()
            elif token.value == 'print':
                return self.parse_print()
            elif token.value == 'if':
                return self.parse_if()
            elif token.value == 'repeat':
                return self.parse_repeat()
            elif token.value == 'function':
                return self.parse_function()
            elif token.value == 'return':
                return self.parse_return()
            elif token.value == 'class':
                return self.parse_class()
        
        # Assignment: identifier = ...
        if self.peek(0).type == 'IDENTIFIER' and self.peek(1) and self.peek(1).value == '=':
            return self.parse_assignment()
        
        # Class Instance Declaration: IDENTIFIER IDENTIFIER = ...
        if self.peek(0).type == 'IDENTIFIER' and self.peek(1) and self.peek(1).type == 'IDENTIFIER':
            return self.parse_var_decl()
        
        # Else it's just an expression (like a function call)
        expr = self.parse_expression()
        self.consume('NEWLINE')
        return expr

    def parse_assignment(self):
        target = self.consume('IDENTIFIER').value
        self.consume('OPERATOR', '=')
        value = self.parse_expression()
        self.consume('NEWLINE')
        return AssignmentNode(target, value)

    def parse_var_decl(self):
        token = self.consume()
        var_type = token.value
        name = self.consume('IDENTIFIER').value
        self.consume('OPERATOR', '=')
        value = self.parse_expression()
        self.consume('NEWLINE')
        return VarDeclNode(var_type, name, value)

    def parse_print(self):
        self.consume('KEYWORD', 'print')
        exprs = []
        exprs.append(self.parse_expression())
        while self.peek() and self.peek().value == ',':
            self.consume('OPERATOR', ',')
            exprs.append(self.parse_expression())
        self.consume('NEWLINE')
        return PrintNode(exprs)

    def parse_if(self):
        self.consume('KEYWORD', 'if')
        condition = self.parse_expression()
        self.consume('OPERATOR', ':')
        self.consume('NEWLINE')
        self.consume('INDENT')
        then_body = self.parse_block()
        self.consume('DEDENT')
        
        else_body = None
        if self.peek() and self.peek().value == 'else':
            self.consume('KEYWORD', 'else')
            self.consume('OPERATOR', ':')
            self.consume('NEWLINE')
            self.consume('INDENT')
            else_body = self.parse_block()
            self.consume('DEDENT')
            
        return IfNode(condition, then_body, else_body)

    def parse_repeat(self):
        self.consume('KEYWORD', 'repeat')
        count = self.parse_expression()
        self.consume('KEYWORD', 'times')
        self.consume('OPERATOR', ':')
        self.consume('NEWLINE')
        self.consume('INDENT')
        body = self.parse_block()
        self.consume('DEDENT')
        return RepeatNode(count, body)

    def parse_function(self):
        self.consume('KEYWORD', 'function')
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        params = []
        if self.peek() and self.peek().type == 'IDENTIFIER':
            params.append(self.consume('IDENTIFIER').value)
            while self.peek() and self.peek().value == ',':
                self.consume('OPERATOR', ',')
                params.append(self.consume('IDENTIFIER').value)
        self.consume('RPAREN')
        self.consume('OPERATOR', '->')
        return_type = self.consume('KEYWORD').value
        self.consume('OPERATOR', ':')
        self.consume('NEWLINE')
        self.consume('INDENT')
        body = self.parse_block()
        self.consume('DEDENT')
        return FunctionNode(name, params, return_type, body)

    def parse_return(self):
        self.consume('KEYWORD', 'return')
        expr = self.parse_expression()
        self.consume('NEWLINE')
        return ReturnNode(expr)

    def parse_class(self):
        self.consume('KEYWORD', 'class')
        name = self.consume('IDENTIFIER').value
        parent = None
        if self.peek() and self.peek().value == 'extends':
            self.consume('KEYWORD', 'extends')
            parent = self.consume('IDENTIFIER').value
        self.consume('OPERATOR', ':')
        self.consume('NEWLINE')
        self.consume('INDENT')
        body = self.parse_block()
        self.consume('DEDENT')
        return ClassNode(name, body, parent)

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        left = self.parse_comparison()
        while self.peek() and self.peek().value in ('==', '!='):
            op = self.consume().value
            right = self.parse_comparison()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.peek() and self.peek().value in ('<', '>', '<=', '>='):
            op = self.consume().value
            right = self.parse_term()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek() and self.peek().value in ('+', '-'):
            op = self.consume().value
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.peek() and self.peek().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_unary()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_unary(self):
        return self.parse_primary()

    def parse_primary(self):
        token = self.consume()
        if token.type == 'NUMBER':
            return LiteralNode(token.value, 'number')
        elif token.type == 'DECIMAL':
            return LiteralNode(token.value, 'decimal')
        elif token.type == 'STRING':
            return LiteralNode(token.value[1:-1], 'string')
        elif token.type == 'KEYWORD' and token.value in ('true', 'false'):
            return LiteralNode(token.value, 'bool')
        elif token.type == 'IDENTIFIER':
            if self.peek() and self.peek().type == 'LPAREN':
                self.consume('LPAREN')
                args = []
                if self.peek() and self.peek().type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.peek() and self.peek().value == ',':
                        self.consume('OPERATOR', ',')
                        args.append(self.parse_expression())
                self.consume('RPAREN')
                return CallNode(token.value, args)
            elif self.peek() and self.peek().value == '.':
                obj = IdentifierNode(token.value)
                while self.peek() and self.peek().value == '.':
                    self.consume('OPERATOR', '.')
                    member = self.consume('IDENTIFIER').value
                    if self.peek() and self.peek().type == 'LPAREN':
                         self.consume('LPAREN')
                         args = []
                         if self.peek() and self.peek().type != 'RPAREN':
                             args.append(self.parse_expression())
                             while self.peek() and self.peek().value == ',':
                                 self.consume('OPERATOR', ',')
                                 args.append(self.parse_expression())
                         self.consume('RPAREN')
                         obj = CallNode(f"{obj.name if isinstance(obj, IdentifierNode) else obj}.{member}", args)
                    else:
                        obj = MemberAccessNode(obj, member)
                return obj
            return IdentifierNode(token.value)
        elif token.type == 'KEYWORD' and token.value == 'new':
            class_name = self.consume('IDENTIFIER').value
            self.consume('LPAREN')
            args = []
            if self.peek() and self.peek().type != 'RPAREN':
                args.append(self.parse_expression())
                while self.peek() and self.peek().value == ',':
                    self.consume('OPERATOR', ',')
                    args.append(self.parse_expression())
            self.consume('RPAREN')
            return NewNode(class_name, args)
        elif token.type == 'LPAREN':
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token {token} at line {token.line}")

# ==========================================
# TRANSPILER
# ==========================================

class Transpiler:
    def __init__(self, ast):
        self.ast = ast
        self.output = []
        self.indent_level = 0
        self.classes = {}
        self.var_types = {} # Symbol table for basic type tracking

    def indent(self):
        return "    " * self.indent_level

    def transpile(self):
        self.output.append("#include <stdio.h>")
        self.output.append("#include <stdlib.h>")
        self.output.append("#include <string.h>")
        self.output.append("#include <stdbool.h>")
        self.output.append("")
        
        # Prototype pass (for functions and classes)
        for node in self.ast.body:
            if isinstance(node, FunctionNode):
                self.output.append(f"{self.map_type(node.return_type)} {node.name}({self.map_params(node.params)});")
            elif isinstance(node, ClassNode):
                self.output.append(f"struct {node.name};")
        
        # Class (Struct) definitions BEFORE main
        for node in self.ast.body:
            if isinstance(node, ClassNode):
                self.output.append(self.visit(node))
        
        self.output.append("")
        
        # Main content
        self.output.append("int main() {")
        self.indent_level += 1
        
        for node in self.ast.body:
            if not isinstance(node, (FunctionNode, ClassNode)):
                self.output.append(self.visit(node) + ";")
        
        self.output.append("return 0;")
        self.indent_level -= 1
        self.output.append("}")
        self.output.append("")
        
        # Functions
        for node in self.ast.body:
            if isinstance(node, FunctionNode):
                self.output.append(f"{self.map_type(node.return_type)} {node.name}({self.map_params(node.params)}) {{")
                self.indent_level += 1
                for stmt in node.body:
                    self.output.append(self.visit(stmt) + ";")
                self.indent_level -= 1
                self.output.append("}")
                self.output.append("")

        return "\n".join(self.output)

    def map_type(self, pss_type):
        mapping = {
            'number': 'int',
            'decimal': 'double',
            'string': 'char*',
            'text': 'char*',
            'bool': 'bool',
            'byte': 'unsigned char',
            'void': 'void'
        }
        if pss_type in mapping:
            return mapping[pss_type]
        return f"struct {pss_type}*"

    def map_params(self, params, first_param=None):
        p_list = []
        if first_param:
            p_list.append(first_param)
        for p in params:
            p_list.append(f"double {p}")
        if not p_list:
            return "void"
        # If there are params after first_param, return them. 
        # Actually, the logic should be: if p_list has items, join them.
        return ", ".join(p_list)

    def visit(self, node):
        if isinstance(node, VarDeclNode):
            self.var_types[node.name] = node.var_type
            return f"{self.indent()}{self.map_type(node.var_type)} {node.name} = {self.visit_expr(node.value)}"
        elif isinstance(node, PrintNode):
            formats = []
            args = []
            for expr in node.expressions:
                fmt, val = self.visit_print_expr(expr)
                formats.append(fmt)
                args.append(val)
            fmt_str = " ".join(formats)
            args_str = ", ".join(args)
            return f'{self.indent()}printf("{fmt_str}\\n", {args_str})'
        elif isinstance(node, IfNode):
            code = f"{self.indent()}if ({self.visit_expr(node.condition)}) {{\n"
            self.indent_level += 1
            for stmt in node.then_body:
                code += self.visit(stmt) + ";\n"
            self.indent_level -= 1
            code += f"{self.indent()}}}"
            if node.else_body:
                code += " else {\n"
                self.indent_level += 1
                for stmt in node.else_body:
                    code += self.visit(stmt) + ";\n"
                self.indent_level -= 1
                code += f"{self.indent()}}}"
            return code
        elif isinstance(node, RepeatNode):
            loop_id = id(node)
            loop_var = f"___i_{loop_id % 10000}"
            code = f"{self.indent()}for (int {loop_var} = 0; {loop_var} < {self.visit_expr(node.count)}; {loop_var}++) {{\n"
            self.indent_level += 1
            for stmt in node.body:
                code += self.visit(stmt) + ";\n"
            self.indent_level -= 1
            code += f"{self.indent()}}}"
            return code
        elif isinstance(node, AssignmentNode):
            return f"{self.indent()}{node.target} = {self.visit_expr(node.value)}"
        elif isinstance(node, ReturnNode):
            return f"{self.indent()}return {self.visit_expr(node.expression)}"
        elif isinstance(node, ClassNode):
            self.classes[node.name] = node
            code = f"struct {node.name} {{\n"
            self.indent_level += 1
            methods = []
            defaults = []
            for stmt in node.body:
                if isinstance(stmt, VarDeclNode):
                    code += f"{self.indent()}{self.map_type(stmt.var_type)} {stmt.name};\n"
                    if stmt.value:
                        defaults.append(stmt)
                elif isinstance(stmt, FunctionNode):
                    methods.append(stmt)
            self.indent_level -= 1
            code += "};\n"
            
            code += f"\nstruct {node.name}* {node.name}_new() {{\n"
            self.indent_level += 1
            code += f"{self.indent()}struct {node.name}* self = (struct {node.name}*)calloc(1, sizeof(struct {node.name}));\n"
            for d in defaults:
                code += f"{self.indent()}self->{d.name} = {self.visit_expr(d.value)};\n"
            code += f"{self.indent()}return self;\n"
            self.indent_level -= 1
            code += "}\n"
            
            # Emit methods as top-level functions
            self.current_class = node.name # Track for visit_call
            for m in methods:
                self.var_types["self"] = node.name
                code += f"\n{self.map_type(m.return_type)} {node.name}_{m.name}({self.map_params(m.params, f'struct {node.name}* self')}) {{\n"
                self.indent_level += 1
                for stmt in m.body:
                    code += self.visit_method_stmt(stmt, node) + ";\n"
                self.indent_level -= 1
                code += "}\n"
            self.current_class = None
            return code
        elif isinstance(node, BinaryOpNode):
            return f"{self.indent()}{self.visit_expr(node)}"
        elif isinstance(node, CallNode):
            return self.indent() + self.visit_call(node)
        return f"{self.indent()}// Unknown node: {type(node).__name__}"

    def visit_expr(self, node):
        if isinstance(node, LiteralNode):
            if node.type == 'string':
                return f'"{node.value}"'
            return str(node.value)
        elif isinstance(node, IdentifierNode):
            return node.name
        elif isinstance(node, BinaryOpNode):
            return f"({self.visit_expr(node.left)} {node.op} {self.visit_expr(node.right)})"
        elif isinstance(node, CallNode):
            return self.visit_call(node)
        elif isinstance(node, NewNode):
            return f"{node.class_name}_new()"
        elif isinstance(node, MemberAccessNode):
            return f"{self.visit_expr(node.object)}->{node.member}"
        return "0"

    def visit_print_expr(self, node):
        val = self.visit_expr(node)
        if isinstance(node, LiteralNode):
            if node.type == 'number': return "%d", val
            if node.type == 'decimal': return "%f", val
            if node.type == 'string': return "%s", val
            if node.type == 'bool': return "%s", f"({val} ? \"true\" : \"false\")"
        if "luas" in val or "pi" in val: return "%f", val
        return "%d", val

    def visit_call(self, node):
        if node.name == 'to_number':
            return f"atoi({self.visit_expr(node.args[0])})"
        if node.name == 'len':
            return f"strlen({self.visit_expr(node.args[0])})"
        if '.' in node.name:
            obj_name, method_name = node.name.split('.')
            class_name = self.var_types.get(obj_name, "Unknown")
            if obj_name == "self":
                # Need a way to know the current class. 
                # For this simple transpiler, we can look at the call stack or pass it.
                # Let's assume the heuristic of checking the current context if possible.
                pass 
            args = [IdentifierNode(obj_name)] + node.args
            args_str = ", ".join([self.visit_expr(a) for a in args])
            return f"{class_name}_{method_name}({args_str})"
        args_str = ", ".join([self.visit_expr(a) for a in node.args])
        return f"{node.name}({args_str})"

    def visit_method_stmt(self, stmt, class_node):
        members = [s.name for s in class_node.body if isinstance(s, VarDeclNode)]
        code = self.visit(stmt)
        parts = re.split(r'("[^"]*")', code)
        new_parts = []
        for part in parts:
            if part.startswith('"'):
                new_parts.append(part)
            else:
                for m in members:
                    part = re.sub(r'\b(?<!self->)' + m + r'\b', f"self->{m}", part)
                new_parts.append(part)
        return "".join(new_parts)

# ==========================================
# CLI ENTRY POINT
# ==========================================

def run_pss(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        code = f.read()

    # Use a temporary directory for compilation to keep the working dir clean
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            transpiler = Transpiler(ast)
            c_code = transpiler.transpile()
            
            c_file = os.path.join(tmpdir, "main.c")
            with open(c_file, 'w') as f:
                f.write(c_code)
                
            exe_file = os.path.join(tmpdir, "main.out")
            
            # Use -O3 for maximum performance (C++ speed)
            try:
                # WSL path conversion for temporary directory
                abs_c_file = os.path.abspath(c_file).replace('\\', '/')
                drive = abs_c_file[0].lower()
                wsl_path = f"/mnt/{drive}{abs_c_file[2:]}"
                
                abs_exe_file = os.path.abspath(exe_file).replace('\\', '/')
                wsl_exe = f"/mnt/{drive}{abs_exe_file[2:]}"
                
                # Use -O3 flag for optimization
                subprocess.run(['wsl', 'gcc', '-O3', wsl_path, '-o', wsl_exe], check=True)
                result = subprocess.run(['wsl', wsl_exe], capture_output=True, text=True)
                print(result.stdout, end="")
                if result.stderr:
                    print("Runtime Errors:", result.stderr)
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to local gcc with -O3
                subprocess.run(['gcc', '-O3', c_file, '-o', exe_file], check=True)
                run_path = exe_file if os.name != 'nt' else exe_file
                result = subprocess.run([run_path], capture_output=True, text=True)
                print(result.stdout, end="")

        except Exception as e:
            print(f"Error: {e}")

def main_cli():
    if len(sys.argv) < 2:
        print("Usage: pss <file.pss>")
        sys.exit(1)
        
    filename = sys.argv[-1] # Usually the last argument
    run_pss(filename)

if __name__ == "__main__":
    main_cli()
