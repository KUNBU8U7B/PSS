#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef enum {
  TOK_FUNC,
  TOK_IF,
  TOK_ELIF,
  TOK_ELSE,
  TOK_WHILE,
  TOK_FOR,
  TOK_DO,
  TOK_RETURN,
  TOK_PRINT,
  TOK_IDENT,
  TOK_NUMBER,
  TOK_STRING,
  TOK_BOOL,
  TOK_NULL,
  TOK_CLASS,
  TOK_INHERITS,
  TOK_SWITCH,
  TOK_CASE,
  TOK_DEFAULT,
  TOK_PLUS,
  TOK_MINUS,
  TOK_STAR,
  TOK_SLASH,
  TOK_PERCENT,
  TOK_POW,
  TOK_PLUSPLUS,
  TOK_MINUSMINUS,
  TOK_PLUSEQ,
  TOK_MINUSEQ,
  TOK_STAREQ,
  TOK_SLASHEQ,
  TOK_PERCENTEQ,
  TOK_POWEQ,
  TOK_EQ,
  TOK_EQEQ,
  TOK_NE,
  TOK_LT,
  TOK_LE,
  TOK_GT,
  TOK_GE,
  TOK_AND,
  TOK_OR,
  TOK_NOT,
  TOK_LPAREN,
  TOK_RPAREN,
  TOK_LBRACKET,
  TOK_RBRACKET,
  TOK_LBRACE,
  TOK_RBRACE,
  TOK_COMMA,
  TOK_COLON,
  TOK_SEMICOLON,
  TOK_INDENT,
  TOK_DEDENT,
  TOK_NEWLINE,
  TOK_EOF,
  TOK_DOT,
  TOK_IN,
  TOK_DEL,
  TOK_BREAK,
  TOK_CONTINUE,
  TOK_CONST,
  TOK_TRY,
  TOK_CATCH,
  TOK_USE,
  TOK_FOREACH
} TokenType;

typedef struct {
  TokenType type;
  char text[256];
  double num_val;
  int is_float;
} Token;
typedef enum { ARCH_X86_64, ARCH_ARM64 } Arch;
Arch target_arch = ARCH_X86_64;

char *src;
int src_pos = 0;
int indent_stack[256] = {0}, indent_depth = 0, pending_dedents = 0,
    pending_indent = 0;
Token next_token() {
  Token t = {TOK_EOF, "", 0, 0};
  if (pending_dedents > 0) {
    pending_dedents--;
    t.type = TOK_DEDENT;
    return t;
  }
  if (pending_indent) {
    pending_indent = 0;
    t.type = TOK_INDENT;
    return t;
  }
  while (src[src_pos] &&
         (src[src_pos] == ' ' || src[src_pos] == '\t' || src[src_pos] == '\r'))
    src_pos++;
  if (!src[src_pos])
    return t;
  if (src[src_pos] == '#') {
    while (src[src_pos] && src[src_pos] != '\n')
      src_pos++;
    return next_token();
  }
  if (src[src_pos] == '/' && src[src_pos + 1] == '*') {
    src_pos += 2;
    while (src[src_pos] && !(src[src_pos] == '*' && src[src_pos + 1] == '/'))
      src_pos++;
    if (src[src_pos])
      src_pos += 2;
    return next_token();
  }
  if (src[src_pos] == '\n') {
    src_pos++;
    t.type = TOK_NEWLINE;
    int spaces = 0;
    while (src[src_pos] == ' ' || src[src_pos] == '\t' ||
           src[src_pos] == '\r' || src[src_pos] == '\n') {
      if (src[src_pos] == '\t')
        spaces += 4;
      else if (src[src_pos] == ' ')
        spaces++;
      else if (src[src_pos] == '\n')
        spaces = 0;
      src_pos++;
    }
    if (src[src_pos] == '#' || !src[src_pos])
      return next_token();
    if (spaces > indent_stack[indent_depth]) {
      indent_stack[++indent_depth] = spaces;
      pending_indent = 1;
    } else if (spaces < indent_stack[indent_depth]) {
      while (indent_depth > 0 && spaces < indent_stack[indent_depth]) {
        indent_depth--;
        pending_dedents++;
      }
    }
    return t;
  }
  if (isalpha(src[src_pos]) || src[src_pos] == '_') {
    int start = src_pos;
    while (isalnum(src[src_pos]) || src[src_pos] == '_')
      src_pos++;
    int len = src_pos - start;
    strncpy(t.text, src + start, len);
    t.text[len] = 0;
    if (!strcmp(t.text, "func"))
      t.type = TOK_FUNC;
    else if (!strcmp(t.text, "if"))
      t.type = TOK_IF;
    else if (!strcmp(t.text, "elif"))
      t.type = TOK_ELIF;
    else if (!strcmp(t.text, "else"))
      t.type = TOK_ELSE;
    else if (!strcmp(t.text, "while"))
      t.type = TOK_WHILE;
    else if (!strcmp(t.text, "for"))
      t.type = TOK_FOR;
    else if (!strcmp(t.text, "do"))
      t.type = TOK_DO;
    else if (!strcmp(t.text, "return"))
      t.type = TOK_RETURN;
    else if (!strcmp(t.text, "print"))
      t.type = TOK_PRINT;
    else if (!strcmp(t.text, "true") || !strcmp(t.text, "false"))
      t.type = TOK_BOOL;
    else if (!strcmp(t.text, "null"))
      t.type = TOK_NULL;
    else if (!strcmp(t.text, "class"))
      t.type = TOK_CLASS;
    else if (!strcmp(t.text, "inherits"))
      t.type = TOK_INHERITS;
    else if (!strcmp(t.text, "switch"))
      t.type = TOK_SWITCH;
    else if (!strcmp(t.text, "case"))
      t.type = TOK_CASE;
    else if (!strcmp(t.text, "default"))
      t.type = TOK_DEFAULT;
    else if (!strcmp(t.text, "and"))
      t.type = TOK_AND;
    else if (!strcmp(t.text, "or"))
      t.type = TOK_OR;
    else if (!strcmp(t.text, "not"))
      t.type = TOK_NOT;
    else if (!strcmp(t.text, "in"))
      t.type = TOK_IN;
    else if (!strcmp(t.text, "del"))
      t.type = TOK_DEL;
    else if (!strcmp(t.text, "break"))
      t.type = TOK_BREAK;
    else if (!strcmp(t.text, "continue"))
      t.type = TOK_CONTINUE;
    else if (!strcmp(t.text, "const"))
      t.type = TOK_CONST;
    else if (!strcmp(t.text, "try"))
      t.type = TOK_TRY;
    else if (!strcmp(t.text, "catch"))
      t.type = TOK_CATCH;
    else if (!strcmp(t.text, "use"))
      t.type = TOK_USE;
    else if (!strcmp(t.text, "foreach"))
      t.type = TOK_FOREACH;
    else
      t.type = TOK_IDENT;
    return t;
  }
  if (isdigit(src[src_pos])) {
    int start = src_pos;
    while (isdigit(src[src_pos]) || src[src_pos] == '.') {
      if (src[src_pos] == '.')
        t.is_float = 1;
      src_pos++;
    }
    int len = src_pos - start;
    strncpy(t.text, src + start, len);
    t.text[len] = 0;
    t.num_val = atof(t.text);
    t.type = TOK_NUMBER;
    return t;
  }
  if (src[src_pos] == '"') {
    src_pos++;
    int len = 0;
    while (src[src_pos] && src[src_pos] != '"') {
      if (src[src_pos] == '\\' && src[src_pos + 1] == 'n') {
        t.text[len++] = '\n';
        src_pos += 2;
      } else {
        t.text[len++] = src[src_pos++];
      }
    }
    t.text[len] = 0;
    src_pos++;
    t.type = TOK_STRING;
    return t;
  }
  char c = src[src_pos++];
  t.text[0] = c;
  t.text[1] = 0;
  if (c == '+') {
    if (src[src_pos] == '+') {
      src_pos++;
      t.type = TOK_PLUSPLUS;
      strcpy(t.text, "++");
    } else if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_PLUSEQ;
      strcpy(t.text, "+=");
    } else
      t.type = TOK_PLUS;
  } else if (c == '-') {
    if (src[src_pos] == '-') {
      src_pos++;
      t.type = TOK_MINUSMINUS;
      strcpy(t.text, "--");
    } else if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_MINUSEQ;
      strcpy(t.text, "-=");
    } else
      t.type = TOK_MINUS;
  } else if (c == '*') {
    if (src[src_pos] == '*') {
      src_pos++;
      if (src[src_pos] == '=') {
        src_pos++;
        t.type = TOK_POWEQ;
        strcpy(t.text, "**=");
      } else {
        t.type = TOK_POW;
        strcpy(t.text, "**");
      }
    } else if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_STAREQ;
      strcpy(t.text, "*=");
    } else
      t.type = TOK_STAR;
  } else if (c == '/') {
    if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_SLASHEQ;
      strcpy(t.text, "/=");
    } else
      t.type = TOK_SLASH;
  } else if (c == '(')
    t.type = TOK_LPAREN;
  else if (c == ')')
    t.type = TOK_RPAREN;
  else if (c == '[')
    t.type = TOK_LBRACKET;
  else if (c == ']')
    t.type = TOK_RBRACKET;
  else if (c == ';')
    t.type = TOK_SEMICOLON;
  else if (c == ',')
    t.type = TOK_COMMA;
  else if (c == '.')
    t.type = TOK_DOT;
  else if (c == '%') {
    if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_PERCENTEQ;
      strcpy(t.text, "%=");
    } else
      t.type = TOK_PERCENT;
  } else if (c == ':')
    t.type = TOK_COLON;
  else if (c == '=') {
    if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_EQEQ;
      strcpy(t.text, "==");
    } else
      t.type = TOK_EQ;
  } else if (c == '!') {
    if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_NE;
      strcpy(t.text, "!=");
    } else
      t.type = TOK_NOT;
  } else if (c == '<') {
    if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_LE;
      strcpy(t.text, "<=");
    } else
      t.type = TOK_LT;
  } else if (c == '>') {
    if (src[src_pos] == '=') {
      src_pos++;
      t.type = TOK_GE;
      strcpy(t.text, ">=");
    } else
      t.type = TOK_GT;
  }
  return t;
}

Token cur_tok;
void next() { cur_tok = next_token(); }
void expect(TokenType type) {
  if (cur_tok.type != type) {
    exit(1);
  }
  next();
}

typedef struct {
  char name[64];
  int offset;
  int is_str;
  int is_list;
  char class_name[64];
} Sym;
Sym syms[2048];
int sym_cnt = 0;
int stack_ptr = 8;
typedef struct {
  char name[64];
  char parent[64];
  char members[64][64];
  int m_is_str[64];
  int member_cnt;
  char methods[64][64];
  int method_cnt;
} Class;
Class classes[128];
int class_cnt = 0;
Class *cur_class = NULL;

int loop_stack_start[256], loop_stack_end[256], loop_depth = 0;

int get_sym(char *name) {
  for (int i = 0; i < sym_cnt; i++)
    if (!strcmp(syms[i].name, name))
      return syms[i].offset;
  strcpy(syms[sym_cnt].name, name);
  syms[sym_cnt].offset = stack_ptr;
  syms[sym_cnt].is_str = syms[sym_cnt].is_list = 0;
  syms[sym_cnt].class_name[0] = 0;
  stack_ptr += 8;
  return syms[sym_cnt++].offset;
}
void set_sym_info(char *name, int is_s, int is_l, char *cname) {
  for (int i = 0; i < sym_cnt; i++)
    if (!strcmp(syms[i].name, name)) {
      syms[i].is_str = is_s;
      syms[i].is_list = is_l;
      if (cname)
        strcpy(syms[i].class_name, cname);
      return;
    }
}
int is_sym_str(char *name) {
  for (int i = 0; i < sym_cnt; i++)
    if (!strcmp(syms[i].name, name))
      return syms[i].is_str;
  return 0;
}
int is_sym_list(char *name) {
  for (int i = 0; i < sym_cnt; i++)
    if (!strcmp(syms[i].name, name))
      return syms[i].is_list;
  return 0;
}
char *get_sym_class(char *name) {
  for (int i = 0; i < sym_cnt; i++)
    if (!strcmp(syms[i].name, name))
      return syms[i].class_name;
  return "";
}

char strings[2048][256];
int str_cnt = 0;
int label_idx = 0;
FILE *out_f;
#define emit(...) fprintf(out_f, __VA_ARGS__)

char *find_method_origin(char *cname, char *mname) {
  while (cname[0]) {
    int cid = -1;
    for (int i = 0; i < class_cnt; i++)
      if (!strcmp(classes[i].name, cname))
        cid = i;
    if (cid == -1)
      break;
    for (int i = 0; i < classes[cid].method_cnt; i++)
      if (!strcmp(classes[cid].methods[i], mname))
        return classes[cid].name;
    cname = classes[cid].parent;
  }
  return NULL;
}

void emit_op(TokenType op) {
  if (target_arch == ARCH_X86_64) {
    emit("  pop %%rbx\n  pop %%rax\n");
    if (op == TOK_PLUS)
      emit("  movq %%rax, %%xmm0\n  movq %%rbx, %%xmm1\n  addsd %%xmm1, %%xmm0\n  movq %%xmm0, %%rax\n");
    else if (op == TOK_MINUS)
      emit("  movq %%rax, %%xmm0\n  movq %%rbx, %%xmm1\n  subsd %%xmm1, %%xmm0\n  movq %%xmm0, %%rax\n");
    else if (op == TOK_STAR)
      emit("  movq %%rax, %%xmm0\n  movq %%rbx, %%xmm1\n  mulsd %%xmm1, %%xmm0\n  movq %%xmm0, %%rax\n");
    else if (op == TOK_SLASH)
      emit("  movq %%rax, %%xmm0\n  movq %%rbx, %%xmm1\n  divsd %%xmm1, %%xmm0\n  movq %%xmm0, %%rax\n");
    else if (op == TOK_PERCENT)
      emit("  xor %%rdx, %%rdx\n  div %%rbx\n  mov %%rdx, %%rax\n");
    else if (op == TOK_POW) {
      int lab1 = ++label_idx, lab2 = ++label_idx;
      emit("  mov %%rax, %%rcx\n  mov $1, %%rax\n.L%d:\n  test %%rbx, %%rbx\n  "
           "jz .L%d\n  imul %%rcx, %%rax\n  dec %%rbx\n  jmp .L%d\n.L%d:\n",
           lab1, lab2, lab1, lab2);
    } else if (op >= TOK_EQEQ && op <= TOK_GE) {
      emit("  movq %%rax, %%xmm0\n  movq %%rbx, %%xmm1\n  ucomisd %%xmm1, %%xmm0\n");
      if (op == TOK_EQEQ)
        emit("  sete %%al\n");
      else if (op == TOK_NE)
        emit("  setne %%al\n");
      else if (op == TOK_LT)
        emit("  setb %%al\n");
      else if (op == TOK_LE)
        emit("  setbe %%al\n");
      else if (op == TOK_GT)
        emit("  seta %%al\n");
      else if (op == TOK_GE)
        emit("  setae %%al\n");
      emit("  movzx %%al, %%rax\n");
      emit("  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n");
    }
    emit("  push %%rax\n");
  } else {
    emit("  ldr x1, [sp], #16\n  ldr x0, [sp], #16\n");
    if (op == TOK_PLUS)
      emit("  fmov d0, x0\n  fmov d1, x1\n  fadd d0, d0, d1\n  fmov x0, d0\n");
    else if (op == TOK_MINUS)
      emit("  fmov d0, x0\n  fmov d1, x1\n  fsub d0, d0, d1\n  fmov x0, d0\n");
    else if (op == TOK_STAR)
      emit("  fmov d0, x0\n  fmov d1, x1\n  fmul d0, d0, d1\n  fmov x0, d0\n");
    else if (op == TOK_SLASH)
      emit("  fmov d0, x0\n  fmov d1, x1\n  fdiv d0, d0, d1\n  fmov x0, d0\n");
    else if (op == TOK_PERCENT)
      emit("  sdiv x2, x0, x1\n  msub x0, x2, x1, x0\n");
    else if (op == TOK_POW) {
      // Simple loop for power in ARM64
      int lab1 = ++label_idx, lab2 = ++label_idx;
      emit("  mov x2, x0\n  mov x0, #1\n.L%d:\n  cbz x1, .L%d\n  mul x0, x0, "
           "x2\n  sub x1, x1, #1\n  b .L%d\n.L%d:\n",
           lab1, lab2, lab1, lab2);
    } else if (op >= TOK_EQEQ && op <= TOK_GE) {
      emit("  cmp x0, x1\n");
      if (op == TOK_EQEQ)
        emit("  cset x0, eq\n");
      else if (op == TOK_NE)
        emit("  cset x0, ne\n");
    }
    emit("  str x0, [sp, #-16]!\n");
  }
}

int last_is_str = 0, last_is_list = 0;
char last_cname[64] = "";
void parse_expr();
void parse_unary() {
  last_is_str = last_is_list = 0;
  last_cname[0] = 0;
  if (cur_tok.type == TOK_NUMBER) {
    if (target_arch == ARCH_X86_64)
      emit("  movabsq $%llu, %%rax\n  push %%rax\n", *(unsigned long long*)&cur_tok.num_val);
    else
      emit("  mov x0, #%llu\n  movk x0, #%llu, lsl #16\n  movk x0, #%llu, lsl #32\n  movk x0, #%llu, lsl #48\n  str x0, [sp, #-16]!\n", (*(unsigned long long*)&cur_tok.num_val) & 0xFFFF, ((*(unsigned long long*)&cur_tok.num_val) >> 16) & 0xFFFF, ((*(unsigned long long*)&cur_tok.num_val) >> 32) & 0xFFFF, ((*(unsigned long long*)&cur_tok.num_val) >> 48) & 0xFFFF);
    next();
  } else if (cur_tok.type == TOK_STRING) {
    strcpy(strings[str_cnt], cur_tok.text);
    last_is_str = 1;
    if (target_arch == ARCH_X86_64)
      emit("  lea .S%d(%%rip), %%rax\n  push %%rax\n", str_cnt++);
    else
      emit("  adrp x0, .S%d\n  add x0, x0, :lo12:.S%d\n  str x0, [sp, #-16]!\n",
           str_cnt, str_cnt++);
    next();
  } else if (cur_tok.type == TOK_NOT) {
    next();
    parse_unary();
    if (target_arch == ARCH_X86_64)
      emit("  pop %%rax\n  test %%rax, %%rax\n  setz %%al\n  movzx %%al, "
           "%%rax\n  "
           "push %%rax\n");
    else
      emit("  ldr x0, [sp], #16\n  cmp x0, #0\n  cset x0, eq\n  str x0, [sp, "
           "#-16]!\n");
  } else if (cur_tok.type == TOK_IDENT) {
    char n[64];
    strcpy(n, cur_tok.text);
    next();
    if (cur_tok.type == TOK_LPAREN) {
      next();
      int ac = 0;
      while (cur_tok.type != TOK_RPAREN) {
        parse_expr();
        ac++;
        if (cur_tok.type == TOK_COMMA)
          next();
      }
      expect(TOK_RPAREN);
      int ic = 0;
      for (int i = 0; i < class_cnt; i++)
        if (!strcmp(classes[i].name, n)) {
          ic = 1;
          strcpy(last_cname, n);
          break;
        }
      if (ic) {
        int cid = -1;
        for (int i = 0; i < class_cnt; i++)
          if (!strcmp(classes[i].name, n))
            cid = i;
        if (target_arch == ARCH_X86_64)
          emit("  mov $%d, %%rdi\n  call pss_malloc\n  push %%rax\n",
               (classes[cid].member_cnt + 1) * 8);
        else
          emit("  mov x0, #%d\n  bl pss_malloc\n  str x0, [sp, #-16]!\n",
               (classes[cid].member_cnt + 1) * 16);
      } else if (!strcmp(n, "input") || !strcmp(n, "int_input") ||
                 !strcmp(n, "float_input")) {
        if (target_arch == ARCH_X86_64) {
          if (ac)
            emit("  pop %%rdi\n");
          else
            emit("  mov $0, %%rdi\n");
          emit("  push %%rdi\n");
          if (!strcmp(n, "input"))
            emit("  call pfunc_input\n");
          else if (!strcmp(n, "int_input"))
            emit("  call pfunc_int_input\n");
          else
            emit("  call pfunc_float_input\n");
          emit("  add $8, %%rsp\n  push %%rax\n");
        } else {
          if (ac)
            emit("  ldr x0, [sp], #16\n");
          else
            emit("  mov x0, #0\n");
          emit("  str x0, [sp, #-16]!\n");
          if (!strcmp(n, "input"))
            emit("  bl pfunc_input\n");
          else if (!strcmp(n, "int_input"))
            emit("  bl pfunc_int_input\n");
          else
            emit("  bl pfunc_float_input\n");
          emit("  add sp, sp, #16\n  str x0, [sp, #-16]!\n");
        }
        last_is_str = !strcmp(n, "input");
      } else if (!strcmp(n, "typeof") || !strcmp(n, "int") ||
                 !strcmp(n, "float") || !strcmp(n, "text") ||
                 !strcmp(n, "bool")) {
        if (!strcmp(n, "text"))
          last_is_str = 1;
        if (!strcmp(n, "int")) {
          if (target_arch == ARCH_X86_64) emit("  pop %%rax\n  movq %%rax, %%xmm0\n  cvttsd2si %%xmm0, %%rax\n  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n  push %%rax\n");
          else emit("  ldr x0, [sp], #16\n  fmov d0, x0\n  fcvtns x0, d0\n  scvtf d0, x0\n  fmov x0, d0\n  str x0, [sp, #-16]!\n");
        } else if (!strcmp(n, "bool")) {
          if (target_arch == ARCH_X86_64) emit("  pop %%rax\n  test %%rax, %%rax\n  setnz %%al\n  movzx %%al, %%rax\n  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n  push %%rax\n");
          else emit("  ldr x0, [sp], #16\n  cmp x0, #0\n  cset x0, ne\n  scvtf d0, x0\n  fmov x0, d0\n  str x0, [sp, #-16]!\n");
        } else if (!strcmp(n, "typeof")) {
          if (target_arch == ARCH_X86_64) emit("  pop %%rax\n  push $1\n");
          else emit("  ldr x0, [sp], #16\n  mov x0, #1\n  str x0, [sp, #-16]!\n");
        }
      } else {
        if (target_arch == ARCH_X86_64)
          emit("  call pfunc_%s\n  add $%d, %%rsp\n  push %%rax\n", n, ac * 8);
        else
          emit("  bl pfunc_%s\n  add sp, sp, #%d\n  str x0, [sp, #-16]!\n", n,
               ac * 16);
      }
    } else if (cur_tok.type == TOK_LBRACKET) {
      next();
      parse_expr();
      expect(TOK_RBRACKET);
      int o = get_sym(n);
      if (target_arch == ARCH_X86_64)
        emit("  pop %%rcx\n  movq -%d(%%rbp), %%rax\n  movq 16(%%rax, %%rcx, "
             "8), %%rax\n  push %%rax\n",
             o);
      else
        emit("  ldr x0, [sp], #16\n  sub x1, x29, #%d\n  ldr x2, [x1]\n  add "
             "x2, x2, #16\n  ldr x0, [x2, x0, lsl #3]\n  str x0, [sp, "
             "#-16]!\n",
             o);
    } else {
      int o = get_sym(n);
      last_is_str = is_sym_str(n);
      last_is_list = is_sym_list(n);
      strcpy(last_cname, get_sym_class(n));
      if (target_arch == ARCH_X86_64)
        emit("  pushq -%d(%%rbp)\n", o);
      else
        emit("  sub x1, x29, #%d\n  ldr x0, [x1]\n  str x0, [sp, #-16]!\n", o);
    }
    while (cur_tok.type == TOK_DOT) {
      next();
      char mn[64];
      strcpy(mn, cur_tok.text);
      next();
      if (cur_tok.type == TOK_LPAREN) {
        next();
        int ac = 0;
        while (cur_tok.type != TOK_RPAREN) {
          parse_expr();
          ac++;
          if (cur_tok.type == TOK_COMMA)
            next();
        }
        expect(TOK_RPAREN);
        if (last_is_list) {
          if (!strcmp(mn, "add")) {
            if (target_arch == ARCH_X86_64)
              emit("  pop %%rsi\n  pop %%rdi\n  call pss_list_add\n  push "
                   "$0\n");
            else
              emit("  ldr x1, [sp], #16\n  ldr x0, [sp], #16\n  bl "
                   "pss_list_add\n  str xzr, [sp, #-16]!\n");
          } else if (!strcmp(mn, "remove")) {
            if (target_arch == ARCH_X86_64)
              emit("  pop %%rsi\n  pop %%rdi\n  call pss_list_remove\n  push "
                   "$0\n");
            else
              emit("  ldr x1, [sp], #16\n  ldr x0, [sp], #16\n  bl "
                   "pss_list_remove\n  str xzr, [sp, #-16]!\n");
          }
        } else if (last_cname[0]) {
          char *orig = find_method_origin(last_cname, mn);
          if (target_arch == ARCH_X86_64)
            emit("  call pfunc_%s_%s\n  add $%d, %%rsp\n  push %%rax\n",
                 orig ? orig : last_cname, mn, (ac + 1) * 8);
          else
            emit("  bl pfunc_%s_%s\n  add sp, sp, #%d\n  str x0, [sp, "
                 "#-16]!\n",
                 orig ? orig : last_cname, mn, (ac + 1) * 16);
        }
      } else if (last_is_list && !strcmp(mn, "length")) {
        if (target_arch == ARCH_X86_64)
          emit("  pop %%rax\n  pushq (%%rax)\n");
        else
          emit("  ldr x0, [sp], #16\n  ldr x0, [x0]\n  str x0, [sp, #-16]!\n");
        last_is_list = 0;
      } else if (last_cname[0]) {
        int cid = -1;
        for (int i = 0; i < class_cnt; i++)
          if (!strcmp(classes[i].name, last_cname))
            cid = i;
        int mo = -1;
        for (int i = 0; i < classes[cid].member_cnt; i++)
          if (!strcmp(classes[cid].members[i], mn))
            mo = i;
        last_is_str = classes[cid].m_is_str[mo];
        if (target_arch == ARCH_X86_64)
          emit("  pop %%rax\n  pushq %d(%%rax)\n", (mo + 1) * 8);
        else
          emit("  ldr x0, [sp], #16\n  ldr x0, [x0, #%d]\n  str x0, [sp, "
               "#-16]!\n",
               (mo + 1) * 16);
      }
    }
  } else if (cur_tok.type == TOK_LBRACKET) {
    next();
    int its = 0;
    while (cur_tok.type != TOK_RBRACKET) {
      parse_expr();
      its++;
      if (cur_tok.type == TOK_COMMA)
        next();
    }
    expect(TOK_RBRACKET);
    last_is_list = 1;
    if (target_arch == ARCH_X86_64) {
      emit("  mov $%d, %%rdi\n  call pss_list_new\n", its);
      for (int i = its - 1; i >= 0; i--)
        emit("  pop %%rcx\n  movq %%rcx, %d(%%rax)\n", 16 + i * 8);
      emit("  push %%rax\n");
    } else {
      emit("  mov x0, #%d\n  bl pss_list_new\n", its);
      for (int i = its - 1; i >= 0; i--)
        emit("  ldr x1, [sp], #16\n  str x1, [x0, #%d]\n", 16 + i * 8);
      emit("  str x0, [sp, #-16]!\n");
    }
  } else if (cur_tok.type == TOK_BOOL) {
    int v = !strcmp(cur_tok.text, "true") ? 1 : 0;
    if (target_arch == ARCH_X86_64)
      emit("  push $%d\n", v);
    else
      emit("  mov x0, #%d\n  str x0, [sp, #-16]!\n", v);
    next();
  } else if (cur_tok.type == TOK_NULL) {
    if (target_arch == ARCH_X86_64)
      emit("  push $0\n");
    else
      emit("  str xzr, [sp, #-16]!\n");
    next();
  } else if (cur_tok.type == TOK_LPAREN) {
    next();
    parse_expr();
    expect(TOK_RPAREN);
  }
  return;
}

void parse_power() {
  parse_unary();
  while (cur_tok.type == TOK_POW) {
    TokenType op = cur_tok.type;
    next();
    parse_unary();
    emit_op(op);
  }
}
void parse_term() {
  parse_power();
  while (cur_tok.type == TOK_STAR || cur_tok.type == TOK_SLASH ||
         cur_tok.type == TOK_PERCENT) {
    TokenType op = cur_tok.type;
    next();
    parse_power();
    emit_op(op);
  }
}
void parse_sum() {
  parse_term();
  while (cur_tok.type == TOK_PLUS || cur_tok.type == TOK_MINUS) {
    TokenType op = cur_tok.type;
    next();
    parse_term();
    emit_op(op);
  }
}
void parse_rel() {
  parse_sum();
  while (cur_tok.type >= TOK_EQEQ && cur_tok.type <= TOK_GE) {
    TokenType op = cur_tok.type;
    next();
    parse_sum();
    emit_op(op);
  }
}
void parse_expr() {
  parse_rel();
  while (cur_tok.type == TOK_AND || cur_tok.type == TOK_OR) {
    TokenType op = cur_tok.type;
    int next_lab = ++label_idx;
    if (op == TOK_AND) {
      if (target_arch == ARCH_X86_64) {
        emit("  pop %%rax\n  test %%rax, %%rax\n  jz .L%d\n", next_lab);
      } else {
        emit("  ldr x0, [sp], #16\n  cbz x0, .L%d\n", next_lab);
      }
    } else {
      if (target_arch == ARCH_X86_64) {
        emit("  pop %%rax\n  test %%rax, %%rax\n  jnz .L%d\n", next_lab);
      } else {
        emit("  ldr x0, [sp], #16\n  cbnz x0, .L%d\n", next_lab);
      }
    }
    next();
    parse_rel();
    if (op == TOK_AND) {
      if (target_arch == ARCH_X86_64) {
        emit("  pop %%rbx\n  test %%rbx, %%rbx\n  setnz %%al\n  movzx %%al, %%rax\n  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n  push %%rax\n  jmp .L%d_end\n.L%d:\n  mov $0, %%rax\n  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n  push %%rax\n.L%d_end:\n", next_lab, next_lab, next_lab);
      } else {
        emit("  ldr x0, [sp], #16\n  cmp x0, #0\n  cset x0, ne\n  scvtf d0, x0\n  fmov x0, d0\n  str x0, [sp, #-16]!\n  b .L%d_end\n.L%d:\n  str xzr, [sp, #-16]!\n.L%d_end:\n", next_lab, next_lab, next_lab);
      }
    } else {
       if (target_arch == ARCH_X86_64) {
        emit("  pop %%rbx\n  test %%rbx, %%rbx\n  setnz %%al\n  movzx %%al, %%rax\n  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n  push %%rax\n  jmp .L%d_end\n.L%d:\n  mov $1, %%rax\n  cvtsi2sd %%rax, %%xmm0\n  movq %%xmm0, %%rax\n  push %%rax\n.L%d_end:\n", next_lab, next_lab, next_lab);
      } else {
        emit("  ldr x0, [sp], #16\n  cmp x0, #0\n  cset x0, ne\n  scvtf d0, x0\n  fmov x0, d0\n  str x0, [sp, #-16]!\n  b .L%d_end\n.L%d:\n  mov x0, #1\n  scvtf d0, x0\n  fmov x0, d0\n  str x0, [sp, #-16]!\n.L%d_end:\n", next_lab, next_lab, next_lab);
      }
    }
  }
}

void parse_stmt();
void parse_block() {
  expect(TOK_SEMICOLON);
  expect(TOK_NEWLINE);
  expect(TOK_INDENT);
  while (cur_tok.type != TOK_DEDENT && cur_tok.type != TOK_EOF)
    parse_stmt();
  expect(TOK_DEDENT);
}
void parse_stmt() {
  while (cur_tok.type == TOK_NEWLINE)
    next();
  if (cur_tok.type == TOK_EOF)
    return;
  if (cur_tok.type == TOK_FUNC) {
    int ls = ++label_idx;
    int old_sym_cnt = sym_cnt, old_stack_ptr = stack_ptr;
    sym_cnt = 0; stack_ptr = 8;
    if (target_arch == ARCH_X86_64)
      emit("  jmp .L%d\n", ls);
    else
      emit("  b .L%d\n", ls);
    sym_cnt = 0; stack_ptr = 8;
    sym_cnt = 0; stack_ptr = 8;
    next();
    char fn[64];
    strcpy(fn, cur_tok.text);
    next();
    if (cur_class)
      strcpy(cur_class->methods[cur_class->method_cnt++], fn);
    expect(TOK_LPAREN);
    char ffn[128];
    if (cur_class)
      sprintf(ffn, "%s_%s", cur_class->name, fn);
    else
      strcpy(ffn, fn);
    int ars[32], ac = 0;
    if (cur_class)
      ars[ac++] = get_sym("self");
    while (cur_tok.type != TOK_RPAREN) {
      ars[ac++] = get_sym(cur_tok.text);
      next();
      if (cur_tok.type == TOK_COMMA)
        next();
    }
    expect(TOK_RPAREN);
    if (cur_class)
      set_sym_info("self", 0, 0, cur_class->name);
    emit("\npfunc_%s:\n", ffn);
    if (target_arch == ARCH_X86_64) {
      emit("  push %%rbp\n  mov %%rsp, %%rbp\n  sub $4096, %%rsp\n");
      for (int i = 0; i < ac; i++)
        emit("  mov %d(%%rbp), %%rax\n  mov %%rax, -%d(%%rbp)\n",
             (ac - i + 1) * 8, ars[i]);
    } else {
      emit("  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n  sub sp, sp, "
           "#4096\n");
      for (int i = 0; i < ac; i++)
        emit("  ldr x0, [x29, #%d]\n  sub x1, x29, #%d\n  str x0, [x1]\n",
             (ac - i + 1) * 16, ars[i]);
    }
    parse_block();
    sym_cnt = old_sym_cnt; stack_ptr = old_stack_ptr;
    if (target_arch == ARCH_X86_64)
      emit("  leave\n  ret\n.L%d:\n", ls);
    else
      emit("  mov sp, x29\n  ldp x29, x30, [sp], #16\n  ret\n.L%d:\n", ls);
  } else if (cur_tok.type == TOK_CLASS) {
    next();
    char cn[64];
    strcpy(cn, cur_tok.text);
    next();
    Class *c = &classes[class_cnt++];
    strcpy(c->name, cn);
    c->member_cnt = 0;
    c->method_cnt = 0;
    c->parent[0] = 0;
    if (cur_tok.type == TOK_INHERITS) {
      next();
      char pn[64];
      strcpy(pn, cur_tok.text);
      strcpy(c->parent, pn);
      next();
      int pid = -1;
      for (int i = 0; i < class_cnt - 1; i++)
        if (!strcmp(classes[i].name, pn))
          pid = i;
      if (pid != -1) {
        c->member_cnt = classes[pid].member_cnt;
        for (int i = 0; i < c->member_cnt; i++) {
          strcpy(c->members[i], classes[pid].members[i]);
          c->m_is_str[i] = classes[pid].m_is_str[i];
        }
      }
    }
    expect(TOK_SEMICOLON);
    expect(TOK_NEWLINE);
    expect(TOK_INDENT);
    cur_class = c;
    while (cur_tok.type != TOK_DEDENT && cur_tok.type != TOK_EOF) {
      if (cur_tok.type == TOK_FUNC)
        parse_stmt();
      else if (cur_tok.type == TOK_IDENT) {
        strcpy(c->members[c->member_cnt], cur_tok.text);
        next();
        if (cur_tok.type == TOK_EQ) {
          next();
          c->m_is_str[c->member_cnt] = (cur_tok.type == TOK_STRING);
          parse_expr();
        }
        c->member_cnt++;
        while (cur_tok.type == TOK_NEWLINE)
          next();
      } else
        next();
    }
    expect(TOK_DEDENT);
    cur_class = NULL;
  } else if (cur_tok.type == TOK_PRINT) {
    next();
    int fr = 1;
    while (1) {
      if (!fr) {
        if (target_arch == ARCH_X86_64)
          emit("  mov $32, %%rdi\n  call print_char\n");
        else
          emit("  mov x0, #32\n  bl print_char\n");
      }
      parse_expr();
      int is_s = last_is_str;
      if (target_arch == ARCH_X86_64) {
        emit("  pop %%rdi\n");
        if (is_s)
          emit("  call print_str_only\n");
        else
          emit("  call print_num_only\n");
      } else {
        emit("  ldr x0, [sp], #16\n");
        if (is_s)
          emit("  bl print_str_only\n");
        else
          emit("  bl print_num_only\n");
      }
      fr = 0;
      if (cur_tok.type == TOK_COMMA)
        next();
      else
        break;
    }
    if (target_arch == ARCH_X86_64)
      emit("  mov $10, %%rdi\n  call print_char\n");
    else
      emit("  mov x0, #10\n  bl print_char\n");
  } else if (cur_tok.type == TOK_RETURN) {
    next();
    parse_expr();
    if (target_arch == ARCH_X86_64) {
      emit("  pop %%rax\n  leave\n  ret\n");
    } else {
      emit("  ldr x0, [sp], #16\n  mov sp, x29\n  ldp x29, x30, [sp], #16\n  "
           "ret\n");
    }
  } else if (cur_tok.type == TOK_SWITCH) {
    next();
    parse_expr();
    if (target_arch == ARCH_X86_64)
      emit("  push %%rax\n");
    else
      emit("  str x0, [sp, #-16]!\n");
    expect(TOK_SEMICOLON);
    while (cur_tok.type == TOK_NEWLINE)
      next();
    expect(TOK_INDENT);
    int end_lab = ++label_idx;
    while (cur_tok.type == TOK_CASE) {
      next();
      int val = (int)cur_tok.num_val;
      next();
      expect(TOK_SEMICOLON);
      int next_lab = ++label_idx;
      if (target_arch == ARCH_X86_64)
        emit("  pop %%rax\n  push %%rax\n  cmp $%d, %%eax\n  jne .L%d\n", val,
             next_lab);
      else
        emit("  ldr x0, [sp]\n  cmp x0, #%d\n  b.ne .L%d\n", val, next_lab);
      while (cur_tok.type == TOK_NEWLINE)
        next();
      if (cur_tok.type == TOK_INDENT) {
        next();
        while (cur_tok.type != TOK_DEDENT && cur_tok.type != TOK_EOF)
          parse_stmt();
        expect(TOK_DEDENT);
      } else
        parse_stmt();
      if (target_arch == ARCH_X86_64)
        emit("  jmp .L%d\n.L%d:\n", end_lab, next_lab);
      else
        emit("  b .L%d\n.L%d:\n", end_lab, next_lab);
      while (cur_tok.type == TOK_NEWLINE)
        next();
    }
    if (cur_tok.type == TOK_DEFAULT) {
      next();
      expect(TOK_SEMICOLON);
      while (cur_tok.type == TOK_NEWLINE)
        next();
      if (cur_tok.type == TOK_INDENT) {
        next();
        while (cur_tok.type != TOK_DEDENT && cur_tok.type != TOK_EOF)
          parse_stmt();
        expect(TOK_DEDENT);
      } else
        parse_stmt();
    }
    if (target_arch == ARCH_X86_64)
      emit("  add $8, %%rsp\n");
    else
      emit("  add sp, sp, #16\n");
    emit(".L%d:\n", end_lab);
    expect(TOK_DEDENT);
  } else if (cur_tok.type == TOK_DO) {
    int ls = ++label_idx, le = ++label_idx;
    loop_stack_start[loop_depth] = ls;
    loop_stack_end[loop_depth++] = le;
    emit(".L%d:\n", ls);
    next();
    parse_block();
    expect(TOK_WHILE);
    parse_expr();
    if (target_arch == ARCH_X86_64)
      emit("  pop %%rax\n  test %%rax, %%rax\n  jnz .L%d\n", ls);
    else
      emit("  ldr x0, [sp], #16\n  cbnz x0, .L%d\n", ls);
    emit(".L%d:\n", le);
    loop_depth--;
  } else if (cur_tok.type == TOK_BREAK || cur_tok.type == TOK_CONTINUE) {
    if (loop_depth > 0) {
      if (cur_tok.type == TOK_BREAK) {
        if (target_arch == ARCH_X86_64) emit("  jmp .L%d\n", loop_stack_end[loop_depth - 1]);
        else emit("  b .L%d\n", loop_stack_end[loop_depth - 1]);
      } else {
        if (target_arch == ARCH_X86_64) emit("  jmp .L%d\n", loop_stack_start[loop_depth - 1]);
        else emit("  b .L%d\n", loop_stack_start[loop_depth - 1]);
      }
    }
    next();
  } else if (cur_tok.type == TOK_IF) {
    int lf = ++label_idx, le = ++label_idx;
    next();
    parse_expr();
    if (target_arch == ARCH_X86_64)
      emit("  pop %%rax\n  test %%rax, %%rax\n  jz .L%d\n", lf);
    else
      emit("  ldr x0, [sp], #16\n  cbz x0, .L%d\n", lf);
    parse_block();
    if (target_arch == ARCH_X86_64)
      emit("  jmp .L%d\n", le);
    else
      emit("  b .L%d\n", le);
    while (cur_tok.type == TOK_ELIF) {
      emit(".L%d:\n", lf);
      lf = ++label_idx;
      next();
      parse_expr();
      if (target_arch == ARCH_X86_64)
        emit("  pop %%rax\n  test %%rax, %%rax\n  jz .L%d\n", lf);
      else
        emit("  ldr x0, [sp], #16\n  cbz x0, .L%d\n", lf);
      parse_block();
      if (target_arch == ARCH_X86_64)
        emit("  jmp .L%d\n", le);
      else
        emit("  b .L%d\n", le);
    }
    emit(".L%d:\n", lf);
    if (cur_tok.type == TOK_ELSE) {
      next();
      parse_block();
    }
    emit(".L%d:\n", le);
  } else if (cur_tok.type == TOK_WHILE) {
    int ls = ++label_idx, le = ++label_idx;
    loop_stack_start[loop_depth] = ls;
    loop_stack_end[loop_depth++] = le;
    emit(".L%d:\n", ls);
    next();
    parse_expr();
    if (target_arch == ARCH_X86_64)
      emit("  pop %%rax\n  test %%rax, %%rax\n  jz .L%d\n", le);
    else
      emit("  ldr x0, [sp], #16\n  cbz x0, .L%d\n", le);
    parse_block();
    if (target_arch == ARCH_X86_64)
      emit("  jmp .L%d\n.L%d:\n", ls, le);
    else
      emit("  b .L%d\n.L%d:\n", ls, le);
    loop_depth--;
  } else if (cur_tok.type == TOK_FOR) {
    next();
    char vn[64];
    strcpy(vn, cur_tok.text);
    next();
    expect(TOK_IN);
    expect(TOK_IDENT); // range
    expect(TOK_LPAREN);
    parse_expr();
    expect(TOK_RPAREN);
    int vo = get_sym(vn);
    int ls = ++label_idx, le = ++label_idx, li = ++label_idx;
    loop_stack_start[loop_depth] = li;
    loop_stack_end[loop_depth++] = le;
    if (target_arch == ARCH_X86_64) {
      emit("  movq $0, -%d(%%rbp)\n.L%d:\n  pop %%rax\n  push %%rax\n  cmpq "
           "-%d(%%rbp), %%rax\n  jle .L%d\n",
           vo, ls, vo, le);
    } else {
      emit("  sub x1, x29, #%d\n  str xzr, [x1]\n.L%d:\n  ldr x0, [sp]\n  ldr "
           "x1, [x29, #-%d]\n  cmp x1, x0\n  bge .L%d\n",
           vo, ls, vo, le);
    }
    parse_block();
    emit(".L%d:\n", li);
    if (target_arch == ARCH_X86_64) {
      emit("  addq $1, -%d(%%rbp)\n  jmp .L%d\n.L%d:\n  add $8, %%rsp\n", vo,
           ls, le);
    } else {
      emit("  sub x1, x29, #%d\n  ldr x0, [x1]\n  add x0, x0, #1\n  str x0, "
           "[x1]\n  b .L%d\n.L%d:\n  add sp, sp, #16\n",
           vo, ls, le);
    }
    loop_depth--;
  } else if (cur_tok.type == TOK_IDENT) {
    char n[64];
    strcpy(n, cur_tok.text);
    next();
    if (cur_tok.type == TOK_LPAREN) {
      next();
      int ac = 0;
      while (cur_tok.type != TOK_RPAREN) {
        parse_expr();
        ac++;
        if (cur_tok.type == TOK_COMMA)
          next();
      }
      expect(TOK_RPAREN);
      if (!strcmp(n, "input") || !strcmp(n, "int_input") ||
          !strcmp(n, "float_input")) {
        if (ac == 0) {
          if (target_arch == ARCH_X86_64)
            emit("  push $0\n");
          else
            emit("  str xzr, [sp, #-16]!\n");
          ac = 1;
        }
      }
      if (target_arch == ARCH_X86_64)
        emit("  call pfunc_%s\n  add $%d, %%rsp\n", n, ac * 8);
      else
        emit("  bl pfunc_%s\n  add sp, sp, #%d\n", n, ac * 16);
    } else if (cur_tok.type == TOK_DOT) {
      int off = get_sym(n);
      if (target_arch == ARCH_X86_64)
        emit("  pushq -%d(%%rbp)\n", off);
      else
        emit("  sub x1, x29, #%d\n  ldr x0, [x1]\n  str x0, [sp, #-16]!\n",
             off);
      int isl = is_sym_list(n);
      char cname[64];
      strcpy(cname, get_sym_class(n));
      while (cur_tok.type == TOK_DOT) {
        next();
        char mn[64];
        strcpy(mn, cur_tok.text);
        next();
        if (cur_tok.type == TOK_EQ) {
          int cid = -1;
          for (int i = 0; i < class_cnt; i++)
            if (!strcmp(classes[i].name, cname))
              cid = i;
          int mo = -1;
          for (int i = 0; i < classes[cid].member_cnt; i++)
            if (!strcmp(classes[cid].members[i], mn))
              mo = i;
          next();
          parse_expr();
          if (target_arch == ARCH_X86_64)
            emit("  pop %%rcx\n  pop %%rax\n  movq %%rcx, %d(%%rax)\n",
                 (mo + 1) * 8);
          else
            emit("  ldr x1, [sp], #16\n  ldr x0, [sp], #16\n  str x1, [x0, "
                 "#%d]\n",
                 (mo + 1) * 16);
        } else if (cur_tok.type == TOK_LPAREN) {
          next();
          int ac = 0;
          while (cur_tok.type != TOK_RPAREN) {
            parse_expr();
            ac++;
            if (cur_tok.type == TOK_COMMA)
              next();
          }
          expect(TOK_RPAREN);
          if (isl) {
            if (!strcmp(mn, "add")) {
              if (target_arch == ARCH_X86_64)
                emit("  pop %%rsi\n  pop %%rdi\n  call pss_list_add\n");
              else
                emit("  ldr x1, [sp], #16\n  ldr x0, [sp], #16\n  bl "
                     "pss_list_add\n");
            } else if (!strcmp(mn, "remove")) {
              if (target_arch == ARCH_X86_64)
                emit("  pop %%rsi\n  pop %%rdi\n  call pss_list_remove\n");
              else
                emit("  ldr x1, [sp], #16\n  ldr x0, [sp], #16\n  bl "
                     "pss_list_remove\n");
            }
          } else if (cname[0]) {
            char *orig = find_method_origin(cname, mn);
            if (target_arch == ARCH_X86_64)
              emit("  call pfunc_%s_%s\n  add $%d, %%rsp\n",
                   orig ? orig : cname, mn, (ac + 1) * 8);
            else
              emit("  bl pfunc_%s_%s\n  add sp, sp, #%d\n", orig ? orig : cname,
                   mn, (ac + 1) * 16);
          }
        }
      }
    } else if (cur_tok.type == TOK_EQ ||
               cur_tok.type >= TOK_PLUSEQ && cur_tok.type <= TOK_POWEQ) {
      TokenType op = cur_tok.type;
      int off = get_sym(n);
      next();
      parse_expr();
      if (op != TOK_EQ) {
        if (target_arch == ARCH_X86_64) {
          emit("  pop %%rbx\n  movq -%d(%%rbp), %%rax\n", off);
          if (op == TOK_PLUSEQ)
            emit("  add %%rbx, %%rax\n");
          else if (op == TOK_MINUSEQ)
            emit("  sub %%rbx, %%rax\n");
          else if (op == TOK_STAREQ)
            emit("  imul %%rbx, %%rax\n");
          emit("  push %%rax\n");
        } else {
          emit("  ldr x1, [sp], #16\n  sub x0, x29, #%d\n  ldr x0, [x0]\n",
               off);
          if (op == TOK_PLUSEQ)
            emit("  add x0, x0, x1\n");
          else if (op == TOK_MINUSEQ)
            emit("  sub x0, x0, x1\n");
          else if (op == TOK_STAREQ)
            emit("  mul x0, x0, x1\n");
          emit("  str x0, [sp, #-16]!\n");
        }
      }
      set_sym_info(n, last_is_str, last_is_list, last_cname);
      if (target_arch == ARCH_X86_64)
        emit("  pop %%rax\n  movq %%rax, -%d(%%rbp)\n", off);
      else
        emit("  ldr x0, [sp], #16\n  sub x1, x29, #%d\n  str x0, [x1]\n", off);
    } else if (cur_tok.type == TOK_PLUSPLUS || cur_tok.type == TOK_MINUSMINUS) {
      TokenType op = cur_tok.type;
      next();
      int off = get_sym(n);
      if (target_arch == ARCH_X86_64) {
        emit("  movq -%d(%%rbp), %%xmm0\n", off);
        emit("  mov $1, %%rax\n  cvtsi2sd %%rax, %%xmm1\n");
        if (op == TOK_PLUSPLUS)
          emit("  addsd %%xmm1, %%xmm0\n");
        else
          emit("  subsd %%xmm1, %%xmm0\n");
        emit("  movq %%xmm0, -%d(%%rbp)\n", off);
      } else {
        emit("  sub x1, x29, #%d\n  ldr x0, [x1]\n", off);
        emit("  fmov d0, x0\n  mov x2, #1\n  scvtf d1, x2\n");
        if (op == TOK_PLUSPLUS)
          emit("  fadd d0, d0, d1\n");
        else
          emit("  fsub d0, d0, d1\n");
        emit("  fmov x0, d0\n  str x0, [x1]\n");
      }
    }
  } else if (cur_tok.type == TOK_DEL) {
    next();
    char n[64];
    strcpy(n, cur_tok.text);
    next();
    int off = get_sym(n);
    if (target_arch == ARCH_X86_64)
      emit("  movq $0, -%d(%%rbp)\n", off);
    else
      emit("  sub x1, x29, #%d\n  str xzr, [x1]\n", off);
  } else
    next();
  while (cur_tok.type == TOK_NEWLINE)
    next();
}

void emit_header() {
  emit(".text\n.globl _start\n_start:\n");
  if (target_arch == ARCH_X86_64)
    emit("  call main\n  mov $60, %%rax\n  xor %%rdi, %%rdi\n  syscall\n\n");
  else
    emit("  bl main\n  mov x0, #0\n  mov x8, #93\n  svc #0\n\n");
}








void emit_runtime() {
  emit("\n.text\n");
  if (target_arch == ARCH_X86_64) {
    emit("print_num:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  sub $32, %%rsp\n"
         "  movq %%rdi, %%xmm0\n"
         "  cvttsd2si %%xmm0, %%rax\n"
         "  mov %%rax, -8(%%rbp)\n"
         "  mov %%rax, %%rdi\n  call print_int\n"
         "  mov $46, %%rdi\n  call print_char\n"
         "  cvtsi2sd -8(%%rbp), %%xmm1\n"
         "  subsd %%xmm1, %%xmm0\n"
         "  mov $10000, %%rax\n"
         "  cvtsi2sd %%rax, %%xmm1\n"
         "  mulsd %%xmm1, %%xmm0\n"
         "  cvttsd2si %%xmm0, %%rax\n"
         "  test %%rax, %%rax\n  jge .Lfp1\n  neg %%rax\n.Lfp1:\n"
         "  mov %%rax, %%rdi\n  call print_int\n"
         "  leave\n  ret\n"
         "print_int:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  sub $64, %%rsp\n"
         "  test %%rdi, %%rdi\n  jns .Li1\n"
         "  push %%rdi\n"
         "  mov $45, %%rdi\n  call print_char\n"
         "  pop %%rdi\n  neg %%rdi\n.Li1:\n"
         "  mov %%rdi, %%rax\n  mov $10, %%rcx\n  lea 63(%%rsp), %%rsi\n  movb $0, (%%rsi)\n"
         "  test %%rax, %%rax\n  jnz .Lp1\n"
         "  dec %%rsi\n  movb $48, (%%rsi)\n  jmp .Lp2\n"
         "  .Lp1: xor %%rdx, %%rdx\n  div %%rcx\n  add $48, %%rdx\n  dec %%rsi\n  movb %%dl, (%%rsi)\n"
         "  test %%rax, %%rax\n  jnz .Lp1\n"
         "  .Lp2: mov %%rsi, %%rdi\n  call print_str_only\n"
         "  leave\n  ret\n"
         "print_num_only: jmp print_num\n"
         "print_str_only:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  mov %%rdi, %%rsi\n  xor %%rdx, %%rdx\n"
         ".Ls1: cmpb $0, (%%rsi, %%rdx)\n  je .Ls2\n  inc %%rdx\n  jmp .Ls1\n"
         ".Ls2: mov $1, %%rax\n  mov $1, %%rdi\n  syscall\n  leave\n  ret\n"
         "print_char:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  push %%rdi\n"
         "  mov $1, %%rax\n  mov $1, %%rdi\n  mov %%rsp, %%rsi\n  mov $1, %%rdx\n  syscall\n"
         "  pop %%rax\n  leave\n  ret\n"
         "pss_malloc:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  push %%r11\n  mov $9, %%rax\n  xor %%rdi, %%rdi\n  mov $4096, %%rsi\n"
         "  mov $3, %%rdx\n  mov $34, %%r10\n  mov $-1, %%r8\n  xor %%r9, %%r9\n  syscall\n"
         "  pop %%r11\n  leave\n  ret\n"
         "pfunc_input:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  push %%r12\n  push %%rbx\n"
         "  mov 16(%%rbp), %%rdi\n  test %%rdi, %%rdi\n  jz .Linp1\n  call print_str_only\n"
         ".Linp1: mov $4096, %%rdi\n  call pss_malloc\n  mov %%rax, %%rbx\n  xor %%r12, %%r12\n"
         ".Linp3: mov $0, %%rax\n  mov $0, %%rdi\n  lea (%%rbx, %%r12), %%rsi\n  mov $1, %%rdx\n  syscall\n"
         "  cmp $1, %%rax\n  jne .Linp2\n"
         "  movb (%%rbx, %%r12), %%al\n  inc %%r12\n  cmp $10, %%al\n  je .Linp2\n  jmp .Linp3\n"
         ".Linp2: movb $0, (%%rbx, %%r12)\n  mov %%rbx, %%rax\n"
         "  pop %%rbx\n  pop %%r12\n  leave\n  ret\n"
         "pfunc_int_input: jmp pfunc_float_input\n"
         "pfunc_float_input:\n"
         "  push %%rbp\n  mov %%rsp, %%rbp\n"
         "  sub $16, %%rsp\n"
         "  mov 16(%%rbp), %%rdi\n  push %%rdi\n  call pfunc_input\n  add $8, %%rsp\n"
         "  mov %%rax, %%rdi\n  xor %%rax, %%rax\n  cvtsi2sd %%rax, %%xmm0\n"
         "  mov $0, %%r8\n"
         "  mov $1, %%r9\n"
         ".Lai_skip: movb (%%rdi), %%al\n  cmp $32, %%al\n  je .Lai_next_p\n  cmp $10, %%al\n  je .Lai_next_p\n  jmp .Lai1\n"
         ".Lai_next_p: inc %%rdi\n  jmp .Lai_skip\n"
         ".Lai1: movb (%%rdi), %%al\n  test %%al, %%al\n  jz .Lai2\n  cmp $10, %%al\n  je .Lai2\n"
         "  cmp $46, %%al\n  jne .Lai3\n  mov $1, %%r8\n  jmp .Lai_next\n"
         ".Lai3: cmp $48, %%al\n  jl .Lai2\n  cmp $57, %%al\n  jg .Lai2\n"
         "  sub $48, %%al\n  movzx %%al, %%rcx\n  cvtsi2sd %%rcx, %%xmm1\n"
         "  test %%r8, %%r8\n  jnz .Lai_frac\n"
         "  mov $10, %%rcx\n  cvtsi2sd %%rcx, %%xmm2\n  mulsd %%xmm2, %%xmm0\n  addsd %%xmm1, %%xmm0\n  jmp .Lai_next\n"
         ".Lai_frac: imul $10, %%r9\n  cvtsi2sd %%r9, %%xmm2\n  divsd %%xmm2, %%xmm1\n  addsd %%xmm1, %%xmm0\n"
         ".Lai_next: inc %%rdi\n  jmp .Lai1\n"
         ".Lai2: movq %%xmm0, %%rax\n  leave\n  ret\n"
         "pss_list_new:\n  push %%rbp\n  mov %%rsp, %%rbp\n  push %%rdi\n  imul $8, %%rdi\n  add $16, %%rdi\n"
         "  mov %%rdi, %%rsi\n  call pss_malloc\n  pop %%rdi\n  mov %%rdi, (%%rax)\n  leave\n  ret\n"
         "pss_list_add:\n  push %%rbp\n  mov %%rsp, %%rbp\n  mov (%%rdi), %%rax\n"
         "  mov %%rsi, 16(%%rdi, %%rax, 8)\n  incq (%%rdi)\n  leave\n  ret\n"
         "pss_list_remove:\n  push %%rbp\n  mov %%rsp, %%rbp\n  mov (%%rdi), %%rcx\n"
         "  lea 16(%%rdi, %%rsi, 8), %%rax\n.Llr1: inc %%rsi\n  cmp %%rsi, %%rcx\n  jle .Llr2\n"
         "  mov 8(%%rax), %%rdx\n  mov %%rdx, (%%rax)\n  add $8, %%rax\n  jmp .Llr1\n.Llr2: decq (%%rdi)\n  leave\n  ret\n");
  } else {
    emit("print_num_only:\n"
         "  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n"
         "  fmov d0, x0\n"
         "  fcvtns x0, d0\n"
         "  bl print_str_only\n"
         "  ldp x29, x30, [sp], #16\n  ret\n");
    emit("print_str_only:\n"
         "  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n"
         "  mov x1, x0\n  mov x2, #0\n"
         ".Ls1: ldrb w3, [x1, x2]\n  cbz w3, .Ls2\n"
         "  add x2, x2, #1\n  b .Ls1\n"
         ".Ls2: mov x0, #1\n  mov x8, #64\n  svc #0\n"
         "  ldp x29, x30, [sp], #16\n  ret\n");
    emit("print_char:\n"
         "  stp x29, x30, [sp, #-16]!\n"
         "  str x0, [sp, #-16]!\n"
         "  mov x0, #1\n  mov x1, sp\n  mov x2, #1\n  mov x8, #64\n  svc #0\n"
         "  add sp, sp, #16\n  ldp x29, x30, [sp], #16\n  ret\n");
    emit("pss_malloc:\n"
         "  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n"
         "  mov x1, x0\n  mov x0, #0\n  mov x2, #3\n  mov x3, #34\n  mov x4, #-1\n  mov x5, #0\n  mov x8, #222\n  svc #0\n"
         "  ldp x29, x30, [sp], #16\n  ret\n");
    emit("pfunc_input:\n"
         "  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n"
         "  stp x19, x20, [sp, #-16]!\n"
         "  ldr x0, [x29, #16]\n  cbz x0, .Linp1\n  bl print_str_only\n"
         ".Linp1: mov x0, #4096\n  bl pss_malloc\n"
         "  mov x19, x0\n  mov x20, #0\n"
         ".Linp3: mov x0, #0\n  add x1, x19, x20\n  mov x2, #1\n  mov x8, #63\n  svc #0\n"
         "  cmp x0, #1\n  bne .Linp2\n  ldrb w1, [x19, x20]\n  add x20, x20, #1\n  cmp w1, #10\n  beq .Linp2\n  b .Linp3\n"
         ".Linp2: add x1, x19, x20\n  mov w2, #0\n  strb w2, [x1]\n  mov x0, x19\n"
         "  ldp x19, x20, [sp], #16\n  ldp x29, x30, [sp], #16\n  ret\n");
    emit("pfunc_int_input: b pfunc_float_input\n");
    emit("pfunc_float_input:\n"
         "  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n"
         "  ldr x0, [x29, #16]\n  str x0, [sp, #-16]!\n  bl pfunc_input\n  add sp, sp, #16\n"
         "  mov x1, x0\n  mov x0, #0\n"
         ".Lai1: ldrb w2, [x1]\n  cmp w2, #10\n  beq .Lai2\n  cbz w2, .Lai2\n"
         "  sub w2, w2, #48\n  mov x3, #10\n  mul x0, x0, x3\n  add x0, x0, x2\n  add x1, x1, #1\n  b .Lai1\n"
         ".Lai2: fmov d0, x0\n  scvtf d0, d0\n  fmov x0, d0\n  ldp x29, x30, [sp], #16\n  ret\n");
    emit("pss_list_new:\n"
         "  stp x29, x30, [sp, #-16]!\n  str x0, [sp, #-16]!\n"
         "  lsl x0, x0, #3\n  add x0, x0, #16\n  bl pss_malloc\n"
         "  ldr x1, [sp], #16\n  str x1, [x0]\n  ldp x29, x30, [sp], #16\n  ret\n");
    emit("pss_list_add:\n"
         "  ldr x2, [x0]\n  add x3, x0, #16\n  str x1, [x3, x2, lsl #3]\n  add x2, x2, #1\n  str x2, [x0]\n  ret\n");
    emit("pss_list_remove:\n"
         "  ldr x2, [x0]\n  add x3, x0, #16\n  add x3, x3, x1, lsl #3\n"
         ".Llr1: add x1, x1, #1\n  cmp x1, x2\n  bge .Llr2\n  ldr x4, [x3, #8]\n"
         "  str x4, [x3]\n  add x3, x3, #8\n  b .Llr1\n.Llr2: sub x2, x2, #1\n  str x2, [x0]\n  ret\n");
  }
}

int main(int argc, char **argv) {
  (void)argc; (void)argv;
  if (argc < 2) return 1;
  int rm = 0; char *pf = NULL;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--run")) rm = 1;
    else pf = argv[i];
  }
#ifdef __aarch64__
  target_arch = ARCH_ARM64;
#endif
  FILE *f = fopen(pf, "rb");
  if (!f) return 1;
  fseek(f, 0, SEEK_END); long s = ftell(f); fseek(f, 0, SEEK_SET);
  src = malloc(s + 2); fread(src, 1, s, f); src[s] = '\n'; src[s + 1] = 0; fclose(f);
  out_f = rm ? fopen(".tmp_pss.s", "w") : stdout;
  emit_header();
  if (target_arch == ARCH_X86_64) emit("main:\n  push %%rbp\n  mov %%rsp, %%rbp\n  sub $65536, %%rsp\n");
  else emit("main:\n  stp x29, x30, [sp, #-16]!\n  mov x29, sp\n  sub sp, sp, #65536\n");
  next(); while (cur_tok.type != TOK_EOF) parse_stmt();
  if (target_arch == ARCH_X86_64) emit("  leave\n  ret\n\n.section .rodata\n");
  else emit("  mov sp, x29\n  ldp x29, x30, [sp], #16\n  ret\n\n.section .rodata\n");
  for (int i = 0; i < str_cnt; i++) {
    emit(".S%d: .asciz \"", i);
    for (char *p = strings[i]; *p; p++) {
      if (*p == '\n') emit("\\n");
      else if (*p == '\"') emit("\\\"");
      else emit("%c", *p);
    }
    emit("\"\n");
  }
  emit_runtime();
  if (rm) {
    if (out_f) fclose(out_f);
    system("gcc -nostdlib -no-pie .tmp_pss.s -o .tmp_pss_bin -g");
    system("./.tmp_pss_bin");
    unlink(".tmp_pss.s"); unlink(".tmp_pss_bin");
  }
  return 0;
}
