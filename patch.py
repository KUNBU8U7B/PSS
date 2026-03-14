
import sys

with open('pss_core.c', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Rename calls
    line = line.replace('call pss_input', 'call pfunc_input')
    line = line.replace('call pss_int_input', 'call pfunc_int_input')
    line = line.replace('bl pss_input', 'bl pfunc_input')
    line = line.replace('bl pss_int_input', 'bl pfunc_int_input')
    
    # NEW x86 input logic (byte-by-byte read, UNIQUE LABELS)
    if 'pfunc_input:\\n  push %%rbp\\n  mov %%rsp, %%rbp' in line and '24(%%rbp)' in line:
         line = '         "pfunc_input:\\n  push %%rbp\\n  mov %%rsp, %%rbp\\n  push %%r12\\n  mov 24(%%rbp), " \n' + \
                '          "%%rdi\\n  test %%rdi, %%rdi\\n  jz .Linp1\\n  call print_str_only\\n.Linp1: " \n' + \
                '          "mov $4096, %%rdi\\n  call pss_malloc\\n  mov %%rax, %%r11\\n  xor %%r12, %%r12\\n" \n' + \
                '          ".Linp3: mov $0, %%rax\\n  mov $0, %%rdi\\n  mov %%r11, %%rsi\\n  add %%r12, %%rsi\\n" \n' + \
                '          "mov $1, %%rdx\\n  syscall\\n  cmp $1, %%rax\\n  jne .Linp2\\n" \n' + \
                '          "movb (%%r11, %%r12), %%al\\n  inc %%r12\\n  cmp $10, %%al\\n  je .Linp2\\n" \n' + \
                '          "jmp .Linp3\\n.Linp2: movb $0, (%%r11, %%r12)\\n  mov %%r11, %%rax\\n  pop %%r12\\n" \n' + \
                '          "leave\\n  ret\\n"\n'
                 
    # Fix x86 int_input logic
    if 'pfunc_int_input:\\n  push %%rbp\\n  mov %%rsp, %%rbp' in line and '.Lai1' in line:
         line = '         "pfunc_int_input:\\n  push %%rbp\\n  mov %%rsp, %%rbp\\n  mov 16(%%rbp), " \n' + \
                '          "%%rdi\\n  push %%rdi\\n  call pfunc_input\\n  add $8, %%rsp\\n " \n' + \
                '          " mov %%rax, %%rdi\\n  xor %%rax, %%rax\\n.Lai1: movb (%%rdi), %%cl\\n  " \n' + \
                '          "cmp $10, %%cl\\n  je .Lai2\\n  test %%cl, %%cl\\n  jz .Lai2\\n  cmp $48, " \n' + \
                '          "%%cl\\n  jl .Lai2\\n  cmp $57, %%cl\\n  jg .Lai2\\n  sub $48, %%cl\\n  " \n' + \
                '          "imul $10, %%rax\\n  movzx %%cl, %%rcx\\n  add %%rcx, %%rax\\n  inc " \n' + \
                '          "%%rdi\\n  jmp .Lai1\\n.Lai2: leave\\n  ret\\n"\n'

    # NEW ARM64 input logic
    if 'pfunc_input:\\n  stp x29, x30, [sp, #-16]!' in line and 'x19, x20' in line:
         line = '         "pfunc_input:\\n  stp x29, x30, [sp, #-16]!\\n  mov x29, sp\\n  stp x19, x20, [sp, #-16]!\\n" \n' + \
                '          "ldr x0, [x29, #16]\\n  cbz x0, .Linp1\\n  bl print_str_only\\n.Linp1: mov x0, #4096\\n" \n' + \
                '          "bl pss_malloc\\n  mov x19, x0\\n  mov x20, #0\\n" \n' + \
                '          ".Linp3: mov x0, #0\\n  add x1, x19, x20\\n  mov x2, #1\\n  mov x8, #63\\n  svc #0\\n" \n' + \
                '          "cmp x0, #1\\n  bne .Linp2\\n  ldrb w1, [x19, x20]\\n  add x20, x20, #1\\n" \n' + \
                '          "cmp w1, #10\\n  beq .Linp2\\n  b .Linp3\\n.Linp2: add x1, x19, x20\\n" \n' + \
                '          "mov w2, #0\\n  strb w2, [x1]\\n  mov x0, x19\\n" \n' + \
                '          "ldp x19, x20, [sp], #16\\n  ldp x29, x30, [sp], #16\\n  ret\\n"\n'

    new_lines.append(line)

with open('pss_core.c', 'w') as f:
    f.writelines(new_lines)
