#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * PSS COMPILER v3.8.3 (Teacher's Choice - Bugfix Edition)
 */

typedef enum { TYPE_INT, TYPE_FLOAT, TYPE_TEXT, TYPE_BOOL, TYPE_NULL } DataType;
typedef struct {
  char name[64];
  int offset;
  DataType type;
  int is_local;
  char reg[8];
} Symbol;
Symbol symbols[8000];
int sym_count = 0;

int label_num = 1;
typedef enum { K_GLOBAL, K_FUNC, K_IF, K_LOOP } ContextType;
typedef struct {
  ContextType type;
  int l_start, l_end, l_next;
  int indent;
  int if_next_emitted;
  int sym_start;
  char loop_var[64];
} Context;
Context ctx_stack[100];
int ctx_depth = 0;

int get_symbol(char *name) {
  char clean[64];
  while (isspace(*name))
    name++;
  int i = 0;
  while (name[i] && !isspace(name[i]) && !strchr(";,+-*/()=", name[i]) &&
         i < 63) {
    clean[i] = name[i];
    i++;
  }
  clean[i] = '\0';
  int start = 0;
  int in_func = 0;
  for (int d = ctx_depth - 1; d >= 0; d--)
    if (ctx_stack[d].type == K_FUNC) {
      start = ctx_stack[d].sym_start;
      in_func = 1;
      break;
    }
  for (int j = sym_count - 1; j >= start; j--)
    if (!strcmp(symbols[j].name, clean))
      return j;
  if (in_func)
    for (int j = start - 1; j >= 0; j--)
      if (!strcmp(symbols[j].name, clean) && !symbols[j].is_local)
        return j;
  strcpy(symbols[sym_count].name, clean);
  symbols[sym_count].is_local = in_func;
  symbols[sym_count].offset =
      (in_func ? (sym_count - start + 1) * 16 : (sym_count + 1) * 16);
  symbols[sym_count].type = TYPE_INT;
  symbols[sym_count].reg[0] = '\0';
  if (!in_func && sym_count < 4)
    sprintf(symbols[sym_count].reg, "r%d", 12 + sym_count);
  return sym_count++;
}

FILE *curr_out;
DataType emit_load(char *operand, char *reg);

DataType emit_load(char *operand, char *reg) {
  if (!operand || !*operand)
    return TYPE_NULL;
  while (isspace(*operand))
    operand++;
  if (isdigit(operand[0]) || (operand[0] == '-' && isdigit(operand[1]))) {
    if (reg)
      fprintf(curr_out, "  mov $%s, %s\n", operand, reg);
    return TYPE_INT;
  }
  if (operand[0] == '"') {
    char s[256];
    sscanf(operand, "\"%[^\"]\"", s);
    int lbl = label_num++;
    fprintf(curr_out,
            "  .section .data\n.S%d: .asciz \"%s\"\n.section .text\n  lea "
            ".S%d(%%rip), %s\n",
            lbl, s, lbl, reg);
    return TYPE_TEXT;
  }
  if (strstr(operand, "input")) {
    char *p = strchr(operand, '"');
    if (p) {
      char msg[256];
      sscanf(p, " \"%[^\"]\"", msg);
      int lbl = label_num++;
      fprintf(curr_out,
              "  .section .data\n.SI%d: .asciz \"%s\"\n.section .text\n  lea "
              ".SI%d(%%rip), %%rdi\n  call print_str\n",
              lbl, msg, lbl);
    }
    fprintf(curr_out,
            "  call flush_buf\n  call get_int\n  if(reg) mov %%rax, %s\n",
            reg ? reg : "%rax");
    return TYPE_INT;
  }
  if (strrchr(operand, '(')) {
    char fv[64], args[256];
    memset(args, 0, 256);
    if (sscanf(operand, " %[^(](%[^)]", fv, args) >= 1) {
      char *st = strdup(args), *a = strtok(st, ",");
      int i = 0;
      char *regs[] = {"%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"};
      while (a && i < 6) {
        emit_load(a, regs[i++]);
        a = strtok(NULL, ",");
      }
      fprintf(curr_out, "  call %s\n", fv);
      if (reg)
        fprintf(curr_out, "  mov %%rax, %s\n", reg);
      free(st);
      return TYPE_INT;
    }
  }
  int idx = get_symbol(operand);
  if (symbols[idx].reg[0]) {
    if (reg)
      fprintf(curr_out, "  mov %%%s, %s\n", symbols[idx].reg, reg);
  } else {
    if (reg)
      fprintf(curr_out, "  mov -%d(%%rbp), %s\n", symbols[idx].offset, reg);
  }
  return symbols[idx].type;
}

DataType emit_expr(char *expr, char *target) {
  if (expr[0] == '"' || strstr(expr, "input"))
    return emit_load(expr, target);
  char v1[64], op[16], v2[64];
  int n = sscanf(expr, " %s %s %[^\n]", v1, op, v2);
  if (n == 3 &&
      (strcmp(op, "+") == 0 || strcmp(op, "-") == 0 || strcmp(op, "*") == 0 ||
       strcmp(op, "/") == 0 || strcmp(op, "==") == 0 || strcmp(op, ">") == 0 ||
       strcmp(op, "<") == 0)) {
    emit_load(v1, "%rax");
    emit_load(v2, "%rbx");
    if (!strcmp(op, "+"))
      fprintf(curr_out, "  add %%rbx, %%rax\n");
    else if (!strcmp(op, "-"))
      fprintf(curr_out, "  sub %%rbx, %%rax\n");
    else if (!strcmp(op, "*"))
      fprintf(curr_out, "  imul %%rbx, %%rax\n");
    else if (!strcmp(op, "/"))
      fprintf(curr_out, "  xor %%rdx, %%rdx\n  idiv %%rbx\n");
    else if (!strcmp(op, "==")) {
      fprintf(curr_out,
              "  cmp %%rbx, %%rax\n  sete %%al\n  movzbl %%al, %%eax\n");
    } else if (!strcmp(op, ">")) {
      fprintf(curr_out,
              "  cmp %%rbx, %%rax\n  setg %%al\n  movzbl %%al, %%eax\n");
    } else if (!strcmp(op, "<")) {
      fprintf(curr_out,
              "  cmp %%rbx, %%rax\n  setl %%al\n  movzbl %%al, %%eax\n");
    }
    fprintf(curr_out, "  mov %%rax, %s\n", target);
    return TYPE_INT;
  }
  return emit_load(expr, target);
}

void close_block() {
  if (ctx_depth <= 0)
    return;
  Context b = ctx_stack[--ctx_depth];
  if (b.type == K_FUNC)
    fprintf(curr_out, "  leave\n  ret\n\n");
  else if (b.type == K_IF) {
    if (!b.if_next_emitted)
      fprintf(curr_out, ".L_ifnext%d:\n", b.l_next);
    fprintf(curr_out, ".L_ifend%d:\n", b.l_end);
  } else if (b.type == K_LOOP) {
    if (b.loop_var[0]) {
      int si = get_symbol(b.loop_var);
      if (symbols[si].reg[0])
        fprintf(curr_out, "  add $1, %%%s\n", symbols[si].reg);
      else
        fprintf(curr_out,
                "  mov -%d(%%rbp), %%rax\n  add $1, %%rax\n  mov %%rax, "
                "-%d(%%rbp)\n",
                symbols[si].offset, symbols[si].offset);
    }
    fprintf(curr_out, "  jmp .L_loop%d\n.L_end%d:\n", b.l_start, b.l_end);
  }
}

int main(int argc, char **argv) {
  if (argc < 2)
    return 1;
  FILE *f = fopen(argv[1], "r");
  if (!f)
    return 1;
  FILE *f_global = tmpfile();
  FILE *f_main = tmpfile();
  curr_out = f_main;
  char line[2048];
  while (fgets(line, sizeof(line), f)) {
    char *p = line;
    int indent = 0;
    while (*p == ' ' || *p == '\t') {
      if (*p == '\t')
        indent += 4;
      else
        indent++;
      p++;
    }
    if (!*p || *p == '#' || *p == '\n')
      continue;
    char *end = p + strlen(p) - 1;
    while (end > p && isspace(*end))
      *end-- = '\0';
    if (*end == ';' || *end == '.')
      *end = '\0';

    while (ctx_depth > 0 && indent <= ctx_stack[ctx_depth - 1].indent &&
           ctx_stack[ctx_depth - 1].type != K_GLOBAL) {
      if (indent == ctx_stack[ctx_depth - 1].indent &&
          (strncmp(p, "elif", 4) == 0 || strncmp(p, "else", 4) == 0))
        break;
      close_block();
      if (ctx_depth == 0)
        curr_out = f_main;
    }
    if (!strncmp(p, "func ", 5)) {
      char fv[64], params[64];
      memset(params, 0, 64);
      sscanf(p + 5, " %[^(](%[^)]", fv, params);
      ctx_stack[ctx_depth++] =
          (Context){.type = K_FUNC, .indent = indent, .sym_start = sym_count};
      curr_out = f_global;
      fprintf(f_global,
              "\n%s:\n  push %%rbp\n  mov %%rsp, %%rbp\n  sub $2048, %%rsp\n",
              fv);
      char *pr = strtok(params, ",");
      int pi = 0;
      char *regs[] = {"%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"};
      while (pr && pi < 6) {
        int si = get_symbol(pr);
        fprintf(f_global, "  mov %s, -%d(%%rbp)\n", regs[pi++],
                symbols[si].offset);
        pr = strtok(NULL, ",");
      }
    } else if (!strncmp(p, "if ", 3) || !strncmp(p, "elif ", 5)) {
      int is_elif = !strncmp(p, "elif ", 5);
      if (is_elif) {
        fprintf(curr_out, "  jmp .L_ifend%d\n.L_ifnext%d:\n",
                ctx_stack[ctx_depth - 1].l_end,
                ctx_stack[ctx_depth - 1].l_next);
        ctx_stack[ctx_depth - 1].l_next = label_num++;
      } else {
        int le = label_num++, ln = label_num++;
        ctx_stack[ctx_depth++] = (Context){
            .type = K_IF, .l_end = le, .l_next = ln, .indent = indent};
      }
      char v1[64], op[8], v2[64];
      char *cond = p + (is_elif ? 5 : 3);
      if (sscanf(cond, " %s %s %[^\n]", v1, op, v2) == 3) {
        emit_load(v1, "%rax");
        emit_load(v2, "%rbx");
        fprintf(curr_out, "  cmp %%rbx, %%rax\n");
        if (!strcmp(op, "=="))
          fprintf(curr_out, "  jne .L_ifnext%d\n",
                  ctx_stack[ctx_depth - 1].l_next);
        else if (!strcmp(op, ">"))
          fprintf(curr_out, "  jle .L_ifnext%d\n",
                  ctx_stack[ctx_depth - 1].l_next);
        else if (!strcmp(op, "<"))
          fprintf(curr_out, "  jge .L_ifnext%d\n",
                  ctx_stack[ctx_depth - 1].l_next);
      }
    } else if (!strncmp(p, "while ", 6)) {
      int ls = label_num++, le = label_num++;
      ctx_stack[ctx_depth++] = (Context){
          .type = K_LOOP, .l_start = ls, .l_end = le, .indent = indent};
      fprintf(curr_out, ".L_loop%d:\n", ls);
      char v1[64], op[8], v2[64];
      if (sscanf(p + 6, " %s %s %[^\n]", v1, op, v2) == 3) {
        emit_load(v1, "%rax");
        emit_load(v2, "%rbx");
        fprintf(curr_out, "  cmp %%rbx, %%rax\n");
        if (!strcmp(op, ">"))
          fprintf(curr_out, "  jle .L_end%d\n", le);
        else if (!strcmp(op, "<"))
          fprintf(curr_out, "  jge .L_end%d\n", le);
        else if (!strcmp(op, "=="))
          fprintf(curr_out, "  jne .L_end%d\n", le);
      }
    } else if (!strncmp(p, "for ", 4)) {
      char v[64], n[64];
      sscanf(p + 4, " %s in range(%[^)]", v, n);
      int si = get_symbol(v);
      if (symbols[si].reg[0])
        fprintf(curr_out, "  mov $0, %%%s\n", symbols[si].reg);
      else
        fprintf(curr_out, "  mov $0, %%rax\n  mov %%rax, -%d(%%rbp)\n",
                symbols[si].offset);
      int ls = label_num++, le = label_num++;
      Context c = {
          .type = K_LOOP, .l_start = ls, .l_end = le, .indent = indent};
      strcpy(c.loop_var, v);
      ctx_stack[ctx_depth++] = c;
      fprintf(curr_out, ".L_loop%d:\n", ls);
      emit_load(n, "%rbx");
      if (symbols[si].reg[0])
        fprintf(curr_out, "  cmp %%rbx, %%%s\n  jge .L_end%d\n",
                symbols[si].reg, le);
      else
        fprintf(curr_out,
                "  mov -%d(%%rbp), %%rax\n  cmp %%rbx, %%rax\n  jge .L_end%d\n",
                symbols[si].offset, le);
    } else if (!strncmp(p, "else", 4)) {
      fprintf(curr_out, "  jmp .L_ifend%d\n.L_ifnext%d:\n",
              ctx_stack[ctx_depth - 1].l_end, ctx_stack[ctx_depth - 1].l_next);
      ctx_stack[ctx_depth - 1].if_next_emitted = 1;
    } else if (!strncmp(p, "print ", 6)) {
      DataType t = emit_expr(p + 6, "%rdi");
      if (t == TYPE_TEXT)
        fprintf(curr_out, "  call print_str\n");
      else
        fprintf(curr_out, "  call print_num\n");
      fprintf(curr_out, "  lea out_buf(%%rip), %%rdi\n  add out_ptr(%%rip), "
                        "%%rdi\n  movb $10, (%%rdi)\n  incq out_ptr(%%rip)\n");
    } else if (strncmp(p, "return ", 7) == 0) {
      emit_expr(p + 7, "%rax");
      fprintf(curr_out, "  leave\n  ret\n");
    } else if (isalpha(*p)) {
      char v[64], o[16];
      sscanf(p, " %s %s", v, o);
      if (!strcmp(o, "=")) {
        DataType t = emit_expr(strchr(p, '=') + 1, "%rax");
        int ix = get_symbol(v);
        symbols[ix].type = t;
        if (symbols[ix].reg[0])
          fprintf(curr_out, "  mov %%rax, %%%s\n", symbols[ix].reg);
        else
          fprintf(curr_out, "  mov %%rax, -%d(%%rbp)\n", symbols[ix].offset);
      } else if (strchr(p, '('))
        emit_load(p, NULL);
    }
  }
  while (ctx_depth > 0)
    close_block();
  printf(
      ".file \"pss\"\n.text\n.section .bss\n  .lcomm out_buf, 262144\n  .lcomm "
      "out_ptr, 8\n  .lcomm in_buf, 16\n.section .text\n.globl _start\n");
  printf("flush_buf: mov $1, %%rax; mov $1, %%rdi; lea out_buf(%%rip), %%rsi; "
         "mov out_ptr(%%rip), %%rdx; test %%rdx, %%rdx; jz .Lf_ret; syscall; "
         "movq $0, out_ptr(%%rip); .Lf_ret: ret\n");
  printf(
      "print_str: push %%rbp; mov %%rsp, %%rbp; mov %%rdi, %%rsi; xor %%rdx, "
      "%%rdx; .Lslen: cmpb $0, (%%rsi, %%rdx); je .Lsdone; inc %%rdx; jmp "
      ".Lslen; .Lsdone: test %%rdx, %%rdx; jz .Lsret; mov out_ptr(%%rip), "
      "%%r8; lea out_buf(%%rip), %%rdi; add %%r8, %%rdi; mov %%rdx, %%rcx; rep "
      "movsb; add %%rdx, out_ptr(%%rip); .Lsret: leave; ret\n");
  printf("print_num: push %%rbp; mov %%rsp, %%rbp; sub $32, %%rsp; mov %%rdi, "
         "%%rax; mov $10, %%rbx; lea 32(%%rsp), %%rcx; .Lp: dec %%rcx; xor "
         "%%rdx, %%rdx; div %%rbx; add $48, %%rdx; movb %%dl, (%%rcx); test "
         "%%rax, %%rax; jnz .Lp; lea 32(%%rsp), %%rdx; sub %%rcx, %%rdx; mov "
         "out_ptr(%%rip), %%r8; lea out_buf(%%rip), %%rdi; add %%r8, %%rdi; "
         "mov %%rcx, %%rsi; mov %%rdx, %%rcx; rep movsb; add %%rdx, "
         "out_ptr(%%rip); leave; ret\n");
  printf("error_exit: .section .data\n.E: .asciz \"Error: Invalid "
         "Input\\n\"\n.section .text\n lea .E(%%rip), %%rdi; call print_str; "
         "call flush_buf; mov $60, %%rax; mov $1, %%rdi; syscall\n");
  printf("get_int: push %%rbx; xor %%rax, %%rax; xor %%rbx, %%rbx; .LiLoopL: "
         "push %%rax; mov $0, %%rax; mov $0, %%rdi; lea in_buf(%%rip), %%rsi; "
         "mov $1, %%rdx; syscall; cmp $1, %%rax; jne .LiEOFL; movzb "
         "in_buf(%%rip), %%rcx; pop %%rax; cmp $10, %%cl; je .LiDoneL; cmp "
         "$45, %%cl; je .LiLoopL; cmp $48, %%cl; jl error_exit; cmp $57, %%cl; "
         "jg error_exit; sub $48, %%cl; imul $10, %%rax; add %%rcx, %%rax; jmp "
         ".LiLoopL; .LiEOFL: pop %%rax; .LiDoneL: pop %%rbx; ret\n");
  rewind(f_global);
  char buf2[1024];
  while (fgets(buf2, 1024, f_global))
    fputs(buf2, stdout);
  printf("\n_start: push %%rbp; mov %%rsp, %%rbp; sub $32768, %%rsp; jmp "
         ".L_main\n\n.L_main:\n");
  rewind(f_main);
  while (fgets(buf2, 1024, f_main))
    fputs(buf2, stdout);
  printf("  call flush_buf\n  mov $60, %%rax\n  xor %%rdi, %%rdi\n  syscall\n");
  return 0;
}
