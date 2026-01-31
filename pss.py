import sys
import subprocess
import os
import re
import tempfile
import shutil

# ==========================================
# ERROR SYSTEM
# ==========================================

class PSSError(Exception):
    def __init__(self, error_type, message, file, line, column=None, code_line=None):
        self.error_type = error_type
        self.message = message
        self.file = file
        self.line = line
        self.column = column
        self.code_line = code_line

    def __str__(self):
        divider = "-" * 40
        res = f"\n{divider}\nFile: {self.file}\nLine: {self.line}\n"
        if self.code_line:
            res += f"\n    {self.code_line}\n"
            if self.column is not None:
                res += "    " + " " * (self.column - 1) + "^\n"
        res += f"{self.error_type}: {self.message}\n{divider}\n"
        return res

class PSSTypeError(PSSError):
    def __init__(self, message, file, line, column=None, code_line=None):
        super().__init__("TypeError", message, file, line, column, code_line)

class PSSNameError(PSSError):
    def __init__(self, message, file, line, column=None, code_line=None):
        super().__init__("NameError", message, file, line, column, code_line)

class PSSSyntaxError(PSSError):
    def __init__(self, message, file, line, column=None, code_line=None):
        super().__init__("SyntaxError", message, file, line, column, code_line)

class PSSRuntimeError(PSSError):
    def __init__(self, message, file, line, column=None, code_line=None):
        super().__init__("RuntimeError", message, file, line, column, code_line)

# ==========================================
# LEXER
# ==========================================

class Token:
    def __init__(self, type, value, line, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

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
    def __init__(self, code, filename="<string>"):
        self.code = code
        self.filename = filename
        self.tokens = []
        self.line = 1
        self.indent_stack = [0]
        self.lines = code.split('\n')

    def tokenize(self):
        # print("DEBUG: Lexer.tokenize start")
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

    def _tokenize_line(self, line_text):
        pos = 0
        while pos < len(line_text.strip()):
            match = None
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(line_text.strip(), pos)
                if match:
                    value = match.group(0)
                    if token_type not in ('WHITESPACE', 'COMMENT'):
                        # Calculate column in original line
                        col = line_text.find(value, pos) + 1
                        self.tokens.append(Token(token_type, value, self.line, col))
                    pos += len(value)
                    break
            if not match:
                raise PSSSyntaxError(f"Illegal character '{line_text.strip()[pos]}'", self.filename, self.line, pos + 1, line_text)

# ==========================================
# PARSER
# ==========================================

class ASTNode:
    def __init__(self, token=None):
        self.token = token

class ProgramNode(ASTNode):
    def __init__(self, name, body, token=None):
        super().__init__(token)
        self.name = name
        self.body = body

class VarDeclNode(ASTNode):
    def __init__(self, var_type, name, value, token=None):
        super().__init__(token)
        self.var_type = var_type
        self.name = name
        self.value = value

class AssignmentNode(ASTNode):
    def __init__(self, target, value, token=None):
        super().__init__(token)
        self.target = target
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, expressions, token=None):
        super().__init__(token)
        self.expressions = expressions

class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None, token=None):
        super().__init__(token)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class RepeatNode(ASTNode):
    def __init__(self, count, body, token=None):
        super().__init__(token)
        self.count = count
        self.body = body

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right, token=None):
        super().__init__(token)
        self.left = left
        self.op = op
        self.right = right

class LiteralNode(ASTNode):
    def __init__(self, value, type, token=None):
        super().__init__(token)
        self.value = value
        self.type = type

class IdentifierNode(ASTNode):
    def __init__(self, name, token=None):
        super().__init__(token)
        self.name = name

class FunctionNode(ASTNode):
    def __init__(self, name, params, return_type, body, token=None):
        super().__init__(token)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expression, token=None):
        super().__init__(token)
        self.expression = expression

class ClassNode(ASTNode):
    def __init__(self, name, body, parent=None, token=None):
        super().__init__(token)
        self.name = name
        self.body = body
        self.parent = parent

class NewNode(ASTNode):
    def __init__(self, class_name, args, token=None):
        super().__init__(token)
        self.class_name = class_name
        self.args = args

class CallNode(ASTNode):
    def __init__(self, name, args, token=None):
        super().__init__(token)
        self.name = name
        self.args = args

class MemberAccessNode(ASTNode):
    def __init__(self, object, member, token=None):
        super().__init__(token)
        self.object = object
        self.member = member

# ==========================================
# TYPE CHECKER
# ==========================================

class TypeChecker:
    def __init__(self, ast, filename, lines):
        self.ast = ast
        self.filename = filename
        self.lines = lines
        self.symbols = {} # name -> type
        self.current_return_type = None

    def error(self, message, node):
        line = node.token.line if node.token else 0
        col = node.token.column if node.token else 0
        code = self.lines[line-1] if 0 < line <= len(self.lines) else ""
        raise PSSTypeError(message, self.filename, line, col, code)

    def check(self):
        for node in self.ast.body:
            self.visit(node)

    def visit(self, node):
        if isinstance(node, VarDeclNode):
            val_type = self.check_expr(node.value)
            expected = node.var_type
            if not self.types_compatible(expected, val_type):
                self.error(f"Cannot assign {val_type} to {expected}", node)
            self.symbols[node.name] = expected
        elif isinstance(node, AssignmentNode):
            if node.target not in self.symbols:
                self.error(f"Variable '{node.target}' not defined", node)
            val_type = self.check_expr(node.value)
            expected = self.symbols[node.target]
            if not self.types_compatible(expected, val_type):
                self.error(f"Cannot assign {val_type} to {expected}", node)
        elif isinstance(node, PrintNode):
            for expr in node.expressions:
                self.check_expr(expr)
        elif isinstance(node, FunctionNode):
            old_symbols = self.symbols.copy()
            self.current_return_type = node.return_type
            for p in node.params:
                self.symbols[p] = "number" # Simplified, default to number for now
            for stmt in node.body:
                self.visit(stmt)
            self.symbols = old_symbols
            self.current_return_type = None

    def check_expr(self, node):
        if isinstance(node, LiteralNode):
            return node.type
        elif isinstance(node, IdentifierNode):
            if node.name not in self.symbols:
                self.error(f"Variable '{node.name}' not defined", node)
            return self.symbols[node.name]
        elif isinstance(node, BinaryOpNode):
            l = self.check_expr(node.left)
            r = self.check_expr(node.right)
            if l == 'string' or r == 'string':
                if node.op == '+': return 'string'
                self.error(f"Invalid operation {node.op} on string", node)
            if l == 'decimal' or r == 'decimal': return 'decimal'
            return 'number'
        return "void"

    def types_compatible(self, expected, actual):
        if expected == actual: return True
        if expected == 'decimal' and actual == 'number': return True
        return False

# ==========================================
# VIRTUAL MACHINE & BYTECODE
# ==========================================

class OpCode:
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    CMP_EQ = "CMP_EQ"
    CMP_LT = "CMP_LT"
    CMP_GT = "CMP_GT"
    JUMP = "JUMP"
    JUMP_IF_FALSE = "JUMP_IF_FALSE"
    PRINT = "PRINT"
    CALL = "CALL"
    RETURN = "RETURN"
    NEW_OBJ = "NEW_OBJ"
    GET_MEMBER = "GET_MEMBER"
    SET_MEMBER = "SET_MEMBER"
    HALT = "HALT"

class BytecodeCompiler:
    def __init__(self, ast):
        self.ast = ast
        self.code = []
        self.constants = []
        self.functions = {} # name -> code
        self.classes = {}   # name -> members

    def emit(self, opcode, arg=None):
        self.code.append((opcode, arg))

    def compile(self):
        for node in self.ast.body:
            self.gen(node)
        self.emit(OpCode.HALT)
        return self.code, self.constants, self.functions, self.classes

    def gen(self, node):
        if isinstance(node, VarDeclNode):
            self.gen_expr(node.value)
            self.emit(OpCode.STORE_VAR, node.name)
        elif isinstance(node, AssignmentNode):
            self.gen_expr(node.value)
            self.emit(OpCode.STORE_VAR, node.target)
        elif isinstance(node, PrintNode):
            for expr in node.expressions:
                self.gen_expr(expr)
            self.emit(OpCode.PRINT, len(node.expressions))
        elif isinstance(node, IfNode):
            self.gen_expr(node.condition)
            jump_false_idx = len(self.code)
            self.emit(OpCode.JUMP_IF_FALSE, 0)
            for stmt in node.then_body:
                self.gen(stmt)
            if node.else_body:
                jump_end_idx = len(self.code)
                self.emit(OpCode.JUMP, 0)
                self.code[jump_false_idx] = (OpCode.JUMP_IF_FALSE, len(self.code))
                for stmt in node.else_body:
                    self.gen(stmt)
                self.code[jump_end_idx] = (OpCode.JUMP, len(self.code))
            else:
                self.code[jump_false_idx] = (OpCode.JUMP_IF_FALSE, len(self.code))
        elif isinstance(node, RepeatNode):
            # i = 0
            # loop:
            #   if i >= count: jump end
            #   body
            #   i = i + 1
            #   jump loop
            # end:
            loop_id = id(node)
            var_name = f"__repeat_{loop_id % 1000}"
            
            # Initial assignment: var = 0
            if 0 not in self.constants: self.constants.append(0)
            self.emit(OpCode.LOAD_CONST, self.constants.index(0))
            self.emit(OpCode.STORE_VAR, var_name)
            
            loop_start = len(self.code)
            
            # Condition: var < count
            self.emit(OpCode.LOAD_VAR, var_name)
            self.gen_expr(node.count)
            self.emit(OpCode.CMP_LT)
            
            jump_end_idx = len(self.code)
            self.emit(OpCode.JUMP_IF_FALSE, 0)
            
            for stmt in node.body:
                self.gen(stmt)
                
            # Increment: var = var + 1
            self.emit(OpCode.LOAD_VAR, var_name)
            if 1 not in self.constants: self.constants.append(1)
            self.emit(OpCode.LOAD_CONST, self.constants.index(1))
            self.emit(OpCode.ADD)
            self.emit(OpCode.STORE_VAR, var_name)
            
            self.emit(OpCode.JUMP, loop_start)
            self.code[jump_end_idx] = (OpCode.JUMP_IF_FALSE, len(self.code))
        elif isinstance(node, FunctionNode):
            # Compile function body separately
            old_code = self.code
            self.code = []
            for stmt in node.body:
                self.gen(stmt)
            self.emit(OpCode.RETURN) # Implicit return
            self.functions[node.name] = (self.code, node.params)
            self.code = old_code
        elif isinstance(node, ReturnNode):
            self.gen_expr(node.expression)
            self.emit(OpCode.RETURN)
        elif isinstance(node, ClassNode):
            members = {}
            for stmt in node.body:
                if isinstance(stmt, VarDeclNode):
                    members[stmt.name] = stmt.value
                elif isinstance(stmt, FunctionNode):
                    # Compile method
                    old_code = self.code
                    self.code = []
                    for s in stmt.body: self.gen(s)
                    self.emit(OpCode.RETURN)
                    members[stmt.name] = (self.code, stmt.params)
                    self.code = old_code
            self.classes[node.name] = members
        elif isinstance(node, (CallNode, MemberAccessNode)):
            self.gen_expr(node)
            # Result of standalone expression is popped if not used
            # But for simplicity in v1.0, we just leave it or use a POP opcode
            # PSS VM current stack management usually expects a result from expr
            # For void functions, we might need to handle this.

    def gen_expr(self, node):
        if isinstance(node, LiteralNode):
            if node.value not in self.constants:
                self.constants.append(node.value)
            self.emit(OpCode.LOAD_CONST, self.constants.index(node.value))
        elif isinstance(node, IdentifierNode):
            self.emit(OpCode.LOAD_VAR, node.name)
        elif isinstance(node, BinaryOpNode):
            self.gen_expr(node.left)
            self.gen_expr(node.right)
            ops = {'+': OpCode.ADD, '-': OpCode.SUB, '*': OpCode.MUL, '/': OpCode.DIV, '==': OpCode.CMP_EQ, '<': OpCode.CMP_LT, '>': OpCode.CMP_GT}
            self.emit(ops[node.op])
        elif isinstance(node, CallNode):
            for arg in node.args:
                self.gen_expr(arg)
            self.emit(OpCode.CALL, (node.name, len(node.args)))
        elif isinstance(node, NewNode):
            self.emit(OpCode.NEW_OBJ, node.class_name)
        elif isinstance(node, MemberAccessNode):
            self.gen_expr(node.object)
            self.emit(OpCode.GET_MEMBER, node.member)

class PSSVM:
    def __init__(self, code, constants, functions=None, classes=None):
        self.code = code
        self.constants = constants
        self.functions = functions or {}
        self.classes = classes or {}
        self.stack = []
        self.frames = [{ "variables": {}, "pc": 0, "code": code }]
        self.current_frame = self.frames[0]

    def run(self):
        while self.current_frame["pc"] < len(self.current_frame["code"]):
            opcode, arg = self.current_frame["code"][self.current_frame["pc"]]
            # print(f"DEBUG Trace: Frame {len(self.frames)} | PC {self.current_frame['pc']} | {opcode} {arg}")
            self.current_frame["pc"] += 1
            if opcode == OpCode.LOAD_CONST:
                self.stack.append(self.constants[arg])
            elif opcode == OpCode.LOAD_VAR:
                # Look in current frame, then self (if method), then global (frames[0])
                val = self.current_frame["variables"].get(arg)
                if val is None and "self" in self.current_frame["variables"]:
                    val = self.current_frame["variables"]["self"]["fields"].get(arg)
                if val is None:
                    val = self.frames[0]["variables"].get(arg, 0)
                self.stack.append(val)
            elif opcode == OpCode.STORE_VAR:
                if arg in self.current_frame["variables"]:
                    self.current_frame["variables"][arg] = self.stack.pop()
                elif "self" in self.current_frame["variables"] and arg in self.current_frame["variables"]["self"]["fields"]:
                    self.current_frame["variables"]["self"]["fields"][arg] = self.stack.pop()
                else:
                    self.current_frame["variables"][arg] = self.stack.pop()
            elif opcode == OpCode.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif opcode == OpCode.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif opcode == OpCode.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif opcode == OpCode.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)
            elif opcode == OpCode.CMP_EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a == b)
            elif opcode == OpCode.CMP_LT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a < b)
            elif opcode == OpCode.CMP_GT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a > b)
            elif opcode == OpCode.JUMP_IF_FALSE:
                condition = self.stack.pop()
                if not condition:
                    self.current_frame["pc"] = arg
            elif opcode == OpCode.SET_MEMBER:
                val = self.stack.pop()
                obj = self.stack.pop()
                if isinstance(obj, dict) and arg in obj["fields"]:
                    obj["fields"][arg] = val
            elif opcode == OpCode.JUMP:
                self.current_frame["pc"] = arg
            elif opcode == OpCode.CALL:
                name, argc = arg
                args = [self.stack.pop() for _ in range(argc)][::-1]
                
                if name in self.functions:
                    f_code, f_params = self.functions[name]
                    new_vars = {p: a for p, a in zip(f_params, args)}
                    self.frames.append({ "variables": new_vars, "pc": 0, "code": f_code })
                    self.current_frame = self.frames[-1]
                elif "." in name:
                    # Method call: obj.method
                    parts = name.split(".")
                    obj_name = parts[0]
                    method_name = parts[1]
                    obj = self.current_frame["variables"].get(obj_name) or self.frames[0]["variables"].get(obj_name)
                    if obj and method_name in obj["methods"]:
                        m_code, m_params = obj["methods"][method_name]
                        new_vars = {p: a for p, a in zip(m_params, args)}
                        new_vars["self"] = obj
                        self.frames.append({ "variables": new_vars, "pc": 0, "code": m_code })
                        self.current_frame = self.frames[-1]
                elif name == "floor": self.stack.append(int(args[0]))
                elif name == "input": self.stack.append(input(args[0] if args else ""))
                else:
                    # print(f"Warning: Unknown function {name}")
                    pass
            elif opcode == OpCode.RETURN:
                result = self.stack.pop() if self.stack else None
                self.frames.pop()
                if not self.frames: break
                self.current_frame = self.frames[-1]
                if result is not None: self.stack.append(result)
            elif opcode == OpCode.NEW_OBJ:
                class_name = arg
                if class_name in self.classes:
                    members = self.classes[class_name]
                    obj = { "fields": {}, "methods": {} }
                    for m_name, m_val in members.items():
                        if isinstance(m_val, tuple): # Method
                            obj["methods"][m_name] = m_val
                        else: # Field (LiteralNode or Expression)
                            # For simplicity in VM v1.0, we just store the initial value if it's literal
                            obj["fields"][m_name] = m_val.value if hasattr(m_val, 'value') else 0
                    self.stack.append(obj)
                else:
                    self.stack.append({ "fields": {}, "methods": {} }) # Fallback
            elif opcode == OpCode.GET_MEMBER:
                obj = self.stack.pop()
                # If obj is a dict (instance)
                if isinstance(obj, dict) and arg in obj["fields"]:
                    self.stack.append(obj["fields"][arg])
                else:
                    self.stack.append(0)
            elif opcode == OpCode.PRINT:
                vals = [self.stack.pop() for _ in range(arg)]
                print(*(vals[::-1]))
            elif opcode == OpCode.HALT:
                break

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
        # print("DEBUG: Parser.parse start")
        token = self.consume('KEYWORD', 'program')
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
        # print(f"DEBUG: Parsed program {name} with {len(body)} statements")
        return ProgramNode(name, body, token)

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
        target_token = self.consume('IDENTIFIER')
        target = target_token.value
        self.consume('OPERATOR', '=')
        value = self.parse_expression()
        self.consume('NEWLINE')
        return AssignmentNode(target, value, target_token)

    def parse_var_decl(self):
        token = self.consume()
        var_type = token.value
        name_token = self.consume('IDENTIFIER')
        name = name_token.value
        self.consume('OPERATOR', '=')
        value = self.parse_expression()
        self.consume('NEWLINE')
        return VarDeclNode(var_type, name, value, token)

    def parse_print(self):
        token = self.consume('KEYWORD', 'print')
        exprs = []
        exprs.append(self.parse_expression())
        while self.peek() and self.peek().value == ',':
            self.consume('OPERATOR', ',')
            exprs.append(self.parse_expression())
        self.consume('NEWLINE')
        return PrintNode(exprs, token)

    def parse_if(self):
        token = self.consume('KEYWORD', 'if')
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
            
        return IfNode(condition, then_body, else_body, token)

    def parse_repeat(self):
        token = self.consume('KEYWORD', 'repeat')
        count = self.parse_expression()
        self.consume('KEYWORD', 'times')
        self.consume('OPERATOR', ':')
        self.consume('NEWLINE')
        self.consume('INDENT')
        body = self.parse_block()
        self.consume('DEDENT')
        return RepeatNode(count, body, token)

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
        token = self.consume('KEYWORD', 'class')
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
        return ClassNode(name, body, parent, token)

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        left = self.parse_comparison()
        while self.peek() and self.peek().value in ('==', '!='):
            token = self.consume()
            op = token.value
            right = self.parse_comparison()
            left = BinaryOpNode(left, op, right, token)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.peek() and self.peek().value in ('<', '>', '<=', '>='):
            token = self.consume()
            op = token.value
            right = self.parse_term()
            left = BinaryOpNode(left, op, right, token)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek() and self.peek().value in ('+', '-'):
            token = self.consume()
            op = token.value
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right, token)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.peek() and self.peek().value in ('*', '/', '%'):
            token = self.consume()
            op = token.value
            right = self.parse_unary()
            left = BinaryOpNode(left, op, right, token)
        return left

    def parse_unary(self):
        return self.parse_primary()

    def parse_primary(self):
        token = self.consume()
        if token.type == 'NUMBER':
            return LiteralNode(int(token.value), 'number', token)
        elif token.type == 'DECIMAL':
            return LiteralNode(float(token.value), 'decimal', token)
        elif token.type == 'STRING':
            return LiteralNode(token.value[1:-1], 'string', token)
        elif token.type == 'KEYWORD' and token.value in ('true', 'false'):
            return LiteralNode(token.value == 'true', 'bool', token)
        elif token.type == 'IDENTIFIER':
            if self.peek() and self.peek().type == 'LPAREN':
                # Function call
                self.consume('LPAREN')
                args = []
                if self.peek() and self.peek().type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.peek() and self.peek().value == ',':
                        self.consume('OPERATOR', ',')
                        args.append(self.parse_expression())
                self.consume('RPAREN')
                return CallNode(token.value, args, token)
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
            return IdentifierNode(token.value, token)
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
            return NewNode(class_name, args, token)
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

def run_pss(file_path, mode="vm"):
    # print(f"DEBUG: run_pss {file_path} mode={mode}")
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        code = f.read()

    try:
        lexer = Lexer(code, filename=file_path)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Phase 2: Type Checking
        checker = TypeChecker(ast, file_path, code.split('\n'))
        # checker.check() # Will enable after full parser refactor

        if mode == "vm":
            # Phase 3: VM Execution
            compiler = BytecodeCompiler(ast)
            vm_code, constants, functions, classes = compiler.compile()
            vm = PSSVM(vm_code, constants, functions, classes)
            vm.run()
        else:
            # High Performance C Mode
            with tempfile.TemporaryDirectory() as tmpdir:
                transpiler = Transpiler(ast)
                c_code = transpiler.transpile()
                c_file = os.path.join(tmpdir, "main.c")
                with open(c_file, 'w') as f: f.write(c_code)
                exe_file = os.path.join(tmpdir, "main.out")
                try:
                    subprocess.run(['gcc', '-O3', c_file, '-o', exe_file], check=True)
                    result = subprocess.run([exe_file], capture_output=True, text=True)
                    print(result.stdout, end="")
                except:
                    print("Error: GCC failed or not found.")

    except PSSError as e:
        print(e)
    except Exception as e:
        import traceback
        traceback.print_exc()

def main_cli():
    import argparse
    parser = argparse.ArgumentParser(description="PSS v1.0 - Simple Programming Script")
    parser.add_argument("file", help="PSS source file")
    parser.add_argument("--c-mode", action="store_true", help="Run in High-Performance C Mode")
    
    args = parser.parse_args()
    mode = "c" if args.c_mode else "vm"
    run_pss(args.file, mode=mode)

if __name__ == "__main__":
    main_cli()
