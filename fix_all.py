
import sys

with open('pss_core.c', 'r') as f:
    content = f.read()

# 1. FIX COMPARISON EMISSION
# We need to change both the comparison instruction and the setcc instructions
old_cmp_block = """      emit("  cmp %%rbx, %%rax\\n");
      if (op == TOK_EQEQ)
        emit("  sete %%al\\n");
      else if (op == TOK_NE)
        emit("  setne %%al\\n");
      else if (op == TOK_LT)
        emit("  setl %%al\\n");
      else if (op == TOK_LE)
        emit("  setle %%al\\n");
      else if (op == TOK_GT)
        emit("  setg %%al\\n");
      else if (op == TOK_GE)
        emit("  setge %%al\\n");"""

new_cmp_block = """      emit("  movq %%rax, %%xmm0\\n  movq %%rbx, %%xmm1\\n  ucomisd %%xmm1, %%xmm0\\n");
      if (op == TOK_EQEQ)
        emit("  sete %%al\\n");
      else if (op == TOK_NE)
        emit("  setne %%al\\n");
      else if (op == TOK_LT)
        emit("  setb %%al\\n");
      else if (op == TOK_LE)
        emit("  setbe %%al\\n");
      else if (op == TOK_GT)
        emit("  seta %%al\\n");
      else if (op == TOK_GE)
        emit("  setae %%al\\n");"""

if old_cmp_block in content:
    content = content.replace(old_cmp_block, new_cmp_block)

# 2. STABILIZE RUNTIME (No Python comments in C strings)
part1_end = content.find('void emit_runtime() {')
if part1_end == -1: part1_end = len(content)

stable_runtime = """
void emit_runtime() {
  emit("\\n.text\\n");
  if (target_arch == ARCH_X86_64) {
    emit("print_num:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  sub $32, %%rsp\\n"
         "  movq %%rdi, %%xmm0\\n"
         "  cvttsd2si %%xmm0, %%rax\\n"
         "  mov %%rax, -8(%%rbp)\\n"
         "  mov %%rax, %%rdi\\n  call print_int\\n"
         "  mov $46, %%rdi\\n  call print_char\\n"
         "  cvtsi2sd -8(%%rbp), %%xmm1\\n"
         "  subsd %%xmm1, %%xmm0\\n"
         "  mov $10000, %%rax\\n"
         "  cvtsi2sd %%rax, %%xmm1\\n"
         "  mulsd %%xmm1, %%xmm0\\n"
         "  cvttsd2si %%xmm0, %%rax\\n"
         "  test %%rax, %%rax\\n  jge .Lfp1\\n  neg %%rax\\n.Lfp1:\\n"
         "  mov %%rax, %%rdi\\n  call print_int\\n"
         "  leave\\n  ret\\n"
         "print_int:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  sub $64, %%rsp\\n"
         "  test %%rdi, %%rdi\\n  jns .Li1\\n"
         "  push %%rdi\\n"
         "  mov $45, %%rdi\\n  call print_char\\n"
         "  pop %%rdi\\n  neg %%rdi\\n.Li1:\\n"
         "  mov %%rdi, %%rax\\n  mov $10, %%rcx\\n  lea 63(%%rsp), %%rsi\\n  movb $0, (%%rsi)\\n"
         "  test %%rax, %%rax\\n  jnz .Lp1\\n"
         "  dec %%rsi\\n  movb $48, (%%rsi)\\n  jmp .Lp2\\n"
         "  .Lp1: xor %%rdx, %%rdx\\n  div %%rcx\\n  add $48, %%rdx\\n  dec %%rsi\\n  movb %%dl, (%%rsi)\\n"
         "  test %%rax, %%rax\\n  jnz .Lp1\\n"
         "  .Lp2: mov %%rsi, %%rdi\\n  call print_str_only\\n"
         "  leave\\n  ret\\n"
         "print_num_only: jmp print_num\\n"
         "print_str_only:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  mov %%rdi, %%rsi\\n  xor %%rdx, %%rdx\\n"
         ".Ls1: cmpb $0, (%%rsi, %%rdx)\\n  je .Ls2\\n  inc %%rdx\\n  jmp .Ls1\\n"
         ".Ls2: mov $1, %%rax\\n  mov $1, %%rdi\\n  syscall\\n  leave\\n  ret\\n"
         "print_char:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  push %%rdi\\n"
         "  mov $1, %%rax\\n  mov $1, %%rdi\\n  mov %%rsp, %%rsi\\n  mov $1, %%rdx\\n  syscall\\n"
         "  pop %%rax\\n  leave\\n  ret\\n"
         "pss_malloc:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  push %%r11\\n  mov $9, %%rax\\n  xor %%rdi, %%rdi\\n  mov $4096, %%rsi\\n"
         "  mov $3, %%rdx\\n  mov $34, %%r10\\n  mov $-1, %%r8\\n  xor %%r9, %%r9\\n  syscall\\n"
         "  pop %%r11\\n  leave\\n  ret\\n"
         "pfunc_input:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  push %%r12\\n  push %%rbx\\n"
         "  mov 16(%%rbp), %%rdi\\n  test %%rdi, %%rdi\\n  jz .Linp1\\n  call print_str_only\\n"
         ".Linp1: mov $4096, %%rdi\\n  call pss_malloc\\n  mov %%rax, %%rbx\\n  xor %%r12, %%r12\\n"
         ".Linp3: mov $0, %%rax\\n  mov $0, %%rdi\\n  lea (%%rbx, %%r12), %%rsi\\n  mov $1, %%rdx\\n  syscall\\n"
         "  cmp $1, %%rax\\n  jne .Linp2\\n"
         "  movb (%%rbx, %%r12), %%al\\n  inc %%r12\\n  cmp $10, %%al\\n  je .Linp2\\n  jmp .Linp3\\n"
         ".Linp2: movb $0, (%%rbx, %%r12)\\n  mov %%rbx, %%rax\\n"
         "  pop %%rbx\\n  pop %%r12\\n  leave\\n  ret\\n"
         "pfunc_int_input: jmp pfunc_float_input\\n"
         "pfunc_float_input:\\n"
         "  push %%rbp\\n  mov %%rsp, %%rbp\\n"
         "  sub $16, %%rsp\\n"
         "  mov 16(%%rbp), %%rdi\\n  push %%rdi\\n  call pfunc_input\\n  add $8, %%rsp\\n"
         "  mov %%rax, %%rdi\\n  xor %%rax, %%rax\\n  cvtsi2sd %%rax, %%xmm0\\n"
         "  mov $0, %%r8\\n"
         "  mov $1, %%r9\\n"
         ".Lai_skip: movb (%%rdi), %%al\\n  cmp $32, %%al\\n  je .Lai_next_p\\n  cmp $10, %%al\\n  je .Lai_next_p\\n  jmp .Lai1\\n"
         ".Lai_next_p: inc %%rdi\\n  jmp .Lai_skip\\n"
         ".Lai1: movb (%%rdi), %%al\\n  test %%al, %%al\\n  jz .Lai2\\n  cmp $10, %%al\\n  je .Lai2\\n"
         "  cmp $46, %%al\\n  jne .Lai3\\n  mov $1, %%r8\\n  jmp .Lai_next\\n"
         ".Lai3: cmp $48, %%al\\n  jl .Lai2\\n  cmp $57, %%al\\n  jg .Lai2\\n"
         "  sub $48, %%al\\n  movzx %%al, %%rcx\\n  cvtsi2sd %%rcx, %%xmm1\\n"
         "  test %%r8, %%r8\\n  jnz .Lai_frac\\n"
         "  mov $10, %%rcx\\n  cvtsi2sd %%rcx, %%xmm2\\n  mulsd %%xmm2, %%xmm0\\n  addsd %%xmm1, %%xmm0\\n  jmp .Lai_next\\n"
         ".Lai_frac: imul $10, %%r9\\n  cvtsi2sd %%r9, %%xmm2\\n  divsd %%xmm2, %%xmm1\\n  addsd %%xmm1, %%xmm0\\n"
         ".Lai_next: inc %%rdi\\n  jmp .Lai1\\n"
         ".Lai2: movq %%xmm0, %%rax\\n  leave\\n  ret\\n"
         "pss_list_new:\\n  push %%rbp\\n  mov %%rsp, %%rbp\\n  push %%rdi\\n  imul $8, %%rdi\\n  add $16, %%rdi\\n"
         "  mov %%rdi, %%rsi\\n  call pss_malloc\\n  pop %%rdi\\n  mov %%rdi, (%%rax)\\n  leave\\n  ret\\n"
         "pss_list_add:\\n  push %%rbp\\n  mov %%rsp, %%rbp\\n  mov (%%rdi), %%rax\\n"
         "  mov %%rsi, 16(%%rdi, %%rax, 8)\\n  incq (%%rdi)\\n  leave\\n  ret\\n"
         "pss_list_remove:\\n  push %%rbp\\n  mov %%rsp, %%rbp\\n  mov (%%rdi), %%rcx\\n"
         "  lea 16(%%rdi, %%rsi, 8), %%rax\\n.Llr1: inc %%rsi\\n  cmp %%rsi, %%rcx\\n  jle .Llr2\\n"
         "  mov 8(%%rax), %%rdx\\n  mov %%rdx, (%%rax)\\n  add $8, %%rax\\n  jmp .Llr1\\n.Llr2: decq (%%rdi)\\n  leave\\n  ret\\n");
  } else {
    emit("print_num_only:\\n"
         "  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n"
         "  fmov d0, x0\\n"
         "  fcvtns x0, d0\\n" # ARM64 implementation simplified for now
         "  bl print_str_only\\n"
         "  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("print_str_only:\\n"
         "  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n"
         "  mov x1, x0\\n  mov x2, #0\\n"
         ".Ls1: ldrb w3, [x1, x2]\\n  cbz w3, .Ls2\\n"
         "  add x2, x2, #1\\n  b .Ls1\\n"
         ".Ls2: mov x0, #1\\n  mov x8, #64\\n  svc #0\\n"
         "  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("print_char:\\n"
         "  stp x29, x30, [sp, #-16]!\\n"
         "  str x0, [sp, #-16]!\\n"
         "  mov x0, #1\\n  mov x1, sp\\n  mov x2, #1\\n  mov x8, #64\\n  svc #0\\n"
         "  add sp, sp, #16\\n  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("pss_malloc:\\n"
         "  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n"
         "  mov x1, x0\\n  mov x0, #0\\n  mov x2, #3\\n  mov x3, #34\\n  mov x4, #-1\\n  mov x5, #0\\n  mov x8, #222\\n  svc #0\\n"
         "  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("pfunc_input:\\n"
         "  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n"
         "  stp x19, x20, [sp, #-16]!\\n"
         "  ldr x0, [x29, #16]\\n  cbz x0, .Linp1\\n  bl print_str_only\\n"
         ".Linp1: mov x0, #4096\\n  bl pss_malloc\\n"
         "  mov x19, x0\\n  mov x20, #0\\n"
         ".Linp3: mov x0, #0\\n  add x1, x19, x20\\n  mov x2, #1\\n  mov x8, #63\\n  svc #0\\n"
         "  cmp x0, #1\\n  bne .Linp2\\n  ldrb w1, [x19, x20]\\n  add x20, x20, #1\\n  cmp w1, #10\\n  beq .Linp2\\n  b .Linp3\\n"
         ".Linp2: add x1, x19, x20\\n  mov w2, #0\\n  strb w2, [x1]\\n  mov x0, x19\\n"
         "  ldp x19, x20, [sp], #16\\n  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("pfunc_int_input: b pfunc_float_input\\n");
    emit("pfunc_float_input:\\n"
         "  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n"
         "  ldr x0, [x29, #16]\\n  str x0, [sp, #-16]!\\n  bl pfunc_input\\n  add sp, sp, #16\\n"
         "  mov x1, x0\\n  mov x0, #0\\n"
         ".Lai1: ldrb w2, [x1]\\n  cmp w2, #10\\n  beq .Lai2\\n  cbz w2, .Lai2\\n"
         "  sub w2, w2, #48\\n  mov x3, #10\\n  mul x0, x0, x3\\n  add x0, x0, x2\\n  add x1, x1, #1\\n  b .Lai1\\n"
         ".Lai2: fmov d0, x0\\n  scvtf d0, d0\\n  fmov x0, d0\\n  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("pss_list_new:\\n"
         "  stp x29, x30, [sp, #-16]!\\n  str x0, [sp, #-16]!\\n"
         "  lsl x0, x0, #3\\n  add x0, x0, #16\\n  bl pss_malloc\\n"
         "  ldr x1, [sp], #16\\n  str x1, [x0]\\n  ldp x29, x30, [sp], #16\\n  ret\\n");
    emit("pss_list_add:\\n"
         "  ldr x2, [x0]\\n  add x3, x0, #16\\n  str x1, [x3, x2, lsl #3]\\n  add x2, x2, #1\\n  str x2, [x0]\\n  ret\\n");
    emit("pss_list_remove:\\n"
         "  ldr x2, [x0]\\n  add x3, x0, #16\\n  add x3, x3, x1, lsl #3\\n"
         ".Llr1: add x1, x1, #1\\n  cmp x1, x2\\n  bge .Llr2\\n  ldr x4, [x3, #8]\\n"
         "  str x4, [x3]\\n  add x3, x3, #8\\n  b .Llr1\\n.Llr2: sub x2, x2, #1\\n  str x2, [x0]\\n  ret\\n");
  }
}

int main(int argc, char **argv) {
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
  src = malloc(s + 2); fread(src, 1, s, f); src[s] = '\\n'; src[s + 1] = 0; fclose(f);
  out_f = rm ? fopen(".tmp_pss.s", \"w\") : stdout;
  emit_header();
  if (target_arch == ARCH_X86_64) emit("main:\\n  push %%rbp\\n  mov %%rsp, %%rbp\\n  sub $65536, %%rsp\\n");
  else emit("main:\\n  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n  sub sp, sp, #65536\\n");
  next(); while (cur_tok.type != TOK_EOF) parse_stmt();
  if (target_arch == ARCH_X86_64) emit("  leave\\n  ret\\n\\n.section .rodata\\n");
  else emit("  mov sp, x29\\n  ldp x29, x30, [sp], #16\\n  ret\\n\\n.section .rodata\\n");
  for (int i = 0; i < str_cnt; i++) {
    emit(".S%d: .asciz \\\"", i);
    for (char *p = strings[i]; *p; p++) {
      if (*p == '\\n') emit("\\\\n");
      else if (*p == '\\\"') emit("\\\\\\\"");
      else emit("%c", *p);
    }
    emit("\\\"\\n");
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
"""

with open('pss_core.c', 'w') as f:
    f.write(content[:part1_end] + stable_runtime)

print("Done")
