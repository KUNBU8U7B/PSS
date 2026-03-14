.text
.globl _start
_start:
  call main
  mov $60, %rax
  xor %rdi, %rdi
  syscall

main:
  push %rbp
  mov %rsp, %rbp
  sub $65536, %rsp
  jmp .L1

pfunc_tambah:
  push %rbp
  mov %rsp, %rbp
  sub $4096, %rsp
  mov 24(%rbp), %rax
  mov %rax, -8(%rbp)
  mov 16(%rbp), %rax
  mov %rax, -16(%rbp)
  pushq -8(%rbp)
  pushq -16(%rbp)
  pop %rbx
  pop %rax
  movq %rax, %xmm0
  movq %rbx, %xmm1
  addsd %xmm1, %xmm0
  movq %xmm0, %rax
  push %rax
  pop %rax
  leave
  ret
  leave
  ret
.L1:
  jmp .L2

pfunc_kurang:
  push %rbp
  mov %rsp, %rbp
  sub $4096, %rsp
  mov 24(%rbp), %rax
  mov %rax, -8(%rbp)
  mov 16(%rbp), %rax
  mov %rax, -16(%rbp)
  pushq -8(%rbp)
  pushq -16(%rbp)
  pop %rbx
  pop %rax
  movq %rax, %xmm0
  movq %rbx, %xmm1
  subsd %xmm1, %xmm0
  movq %xmm0, %rax
  push %rax
  pop %rax
  leave
  ret
  leave
  ret
.L2:
  jmp .L3

pfunc_kali:
  push %rbp
  mov %rsp, %rbp
  sub $4096, %rsp
  mov 24(%rbp), %rax
  mov %rax, -8(%rbp)
  mov 16(%rbp), %rax
  mov %rax, -16(%rbp)
  pushq -8(%rbp)
  pushq -16(%rbp)
  pop %rbx
  pop %rax
  movq %rax, %xmm0
  movq %rbx, %xmm1
  mulsd %xmm1, %xmm0
  movq %xmm0, %rax
  push %rax
  pop %rax
  leave
  ret
  leave
  ret
.L3:
  jmp .L4

pfunc_bagi:
  push %rbp
  mov %rsp, %rbp
  sub $4096, %rsp
  mov 24(%rbp), %rax
  mov %rax, -8(%rbp)
  mov 16(%rbp), %rax
  mov %rax, -16(%rbp)
  pushq -16(%rbp)
  movabsq $0, %rax
  push %rax
  pop %rbx
  pop %rax
  cmp %rbx, %rax
  sete %al
  movzx %al, %rax
  push %rax
  pop %rax
  test %rax, %rax
  jz .L5
  lea .S0(%rip), %rax
  push %rax
  pop %rdi
  call print_str_only
  mov $10, %rdi
  call print_char
  push $0
  pop %rax
  leave
  ret
  jmp .L6
.L5:
  pushq -8(%rbp)
  pushq -16(%rbp)
  pop %rbx
  pop %rax
  movq %rax, %xmm0
  movq %rbx, %xmm1
  divsd %xmm1, %xmm0
  movq %xmm0, %rax
  push %rax
  pop %rax
  leave
  ret
.L6:
  leave
  ret
.L4:
  jmp .L7

pfunc_kalkulator:
  push %rbp
  mov %rsp, %rbp
  sub $4096, %rsp
  lea .S1(%rip), %rax
  push %rax
  pop %rdi
  call print_str_only
  mov $10, %rdi
  call print_char
  mov $0, %rdi
  push %rdi
  call pfunc_int_input
  add $8, %rsp
  push %rax
  pop %rax
  movq %rax, -8(%rbp)
  lea .S2(%rip), %rax
  push %rax
  pop %rdi
  push %rdi
  call pfunc_float_input
  add $8, %rsp
  push %rax
  pop %rax
  movq %rax, -16(%rbp)
  lea .S3(%rip), %rax
  push %rax
  pop %rdi
  push %rdi
  call pfunc_float_input
  add $8, %rsp
  push %rax
  pop %rax
  movq %rax, -24(%rbp)
  pushq -8(%rbp)
  movabsq $4607182418800017408, %rax
  push %rax
  pop %rbx
  pop %rax
  cmp %rbx, %rax
  sete %al
  movzx %al, %rax
  push %rax
  pop %rax
  test %rax, %rax
  jz .L8
  pushq -16(%rbp)
  pushq -24(%rbp)
  call pfunc_tambah
  add $16, %rsp
  push %rax
  pop %rdi
  call print_num_only
  mov $10, %rdi
  call print_char
  jmp .L9
.L8:
  pushq -8(%rbp)
  movabsq $4611686018427387904, %rax
  push %rax
  pop %rbx
  pop %rax
  cmp %rbx, %rax
  sete %al
  movzx %al, %rax
  push %rax
  pop %rax
  test %rax, %rax
  jz .L10
  pushq -16(%rbp)
  pushq -24(%rbp)
  call pfunc_kurang
  add $16, %rsp
  push %rax
  pop %rdi
  call print_num_only
  mov $10, %rdi
  call print_char
  jmp .L9
.L10:
  pushq -8(%rbp)
  movabsq $4613937818241073152, %rax
  push %rax
  pop %rbx
  pop %rax
  cmp %rbx, %rax
  sete %al
  movzx %al, %rax
  push %rax
  pop %rax
  test %rax, %rax
  jz .L11
  pushq -16(%rbp)
  pushq -24(%rbp)
  call pfunc_kali
  add $16, %rsp
  push %rax
  pop %rdi
  call print_num_only
  mov $10, %rdi
  call print_char
  jmp .L9
.L11:
  pushq -8(%rbp)
  movabsq $4616189618054758400, %rax
  push %rax
  pop %rbx
  pop %rax
  cmp %rbx, %rax
  sete %al
  movzx %al, %rax
  push %rax
  pop %rax
  test %rax, %rax
  jz .L12
  pushq -16(%rbp)
  pushq -24(%rbp)
  call pfunc_bagi
  add $16, %rsp
  push %rax
  pop %rdi
  call print_num_only
  mov $10, %rdi
  call print_char
  jmp .L9
.L12:
.L9:
  leave
  ret
.L7:
  call pfunc_kalkulator
  add $0, %rsp
  leave
  ret

.section .rodata
.S0: .asciz "Error: Pembagian dengan nol"
.S1: .asciz "====KALKULATOR====\n1.tambah\n2.kurang\n3.kali\n4.bagi\nmasukan pilihan:"
.S2: .asciz "masukan angka pertama:"
.S3: .asciz "masukan angka kedua:"

.text
print_num:
  push %rbp
  mov %rsp, %rbp
  sub $64, %rsp
  movq %rdi, %xmm0
  cvttsd2si %xmm0, %rax
  mov %rax, %r12
  mov %r12, %rdi
  call print_int
  mov $46, %rdi
  call print_char
  cvtsi2sd %r12, %xmm1
  subsd %xmm1, %xmm0
  movabsq $10000, %rax
  cvtsi2sd %rax, %xmm1
  mulsd %xmm1, %xmm0
  cvttsd2si %xmm0, %rax
  test %rax, %rax
  jge .Lfp1
  neg %rax
.Lfp1:
  mov %rax, %rdi
  call print_int
  leave
  ret
print_int:
  push %rbp
  mov %rsp, %rbp
  sub $64, %rsp
  test %rdi, %rdi
  jns .Li1
  push %rdi
  mov $45, %rdi
  call print_char
  pop %rdi
  neg %rdi
.Li1:
  mov %rdi, %rax
  mov $10, %rcx
  lea 63(%rsp), %rsi
  movb $0, (%rsi)
  .Lp1: xor %rdx, %rdx
  div %rcx
  add $48, %rdx
  dec %rsi
  movb %dl, (%rsi)
  test %rax, %rax
  jnz .Lp1
  mov %rsi, %rdi
  call print_str_only
  leave
  ret
print_num_only: jmp print_num
print_str_only:
  push %rbp
  mov %rsp, %rbp
  mov %rdi, %rsi
  xor %rdx, %rdx
.Ls1: cmpb $0, (%rsi, %rdx)
  je .Ls2
  inc %rdx
  jmp .Ls1
.Ls2: mov $1, %rax
  mov $1, %rdi
  syscall
  leave
  ret
print_char:
  push %rbp
  mov %rsp, %rbp
  push %rdi
  mov $1, %rax
  mov $1, %rdi
  mov %rsp, %rsi
  mov $1, %rdx
  syscall
  add $8, %rsp
  leave
  ret
pss_malloc:
  push %rbp
  mov %rsp, %rbp
  push %r11
  mov $9, %rax
  xor %rdi, %rdi
  mov $4096, %rsi
  mov $3, %rdx
  mov $34, %r10
  mov $-1, %r8
  xor %r9, %r9
  syscall
  pop %r11
  leave
  ret
pfunc_input:
  push %rbp
  mov %rsp, %rbp
  push %r12
  sub $8, %rsp
  mov 16(%rbp), %rdi
  test %rdi, %rdi
  jz .Linp1
  call print_str_only
.Linp1: mov $4096, %rdi
  call pss_malloc
  mov %rax, -16(%rbp)
  xor %r12, %r12
.Linp3: mov $0, %rax
  mov $0, %rdi
  mov -16(%rbp), %rsi
  add %r12, %rsi
  mov $1, %rdx
  syscall
  cmp $1, %rax
  jne .Linp2
  mov -16(%rbp), %rax
  movb (%rax, %r12), %al
  inc %r12
  cmp $10, %al
  je .Linp2
  jmp .Linp3
.Linp2: mov -16(%rbp), %rax
  movb $0, (%rax, %r12)
  add $8, %rsp
  pop %r12
  leave
  ret
pfunc_int_input:
  push %rbp
  mov %rsp, %rbp
  mov 16(%rbp), %rdi
  push %rdi
  call pfunc_float_input
  add $8, %rsp
  leave
  ret
pfunc_float_input:
  push %rbp
  mov %rsp, %rbp
  mov 16(%rbp), %rdi
  push %rdi
  call pfunc_input
  add $8, %rsp
  mov %rax, %rdi
  xor %rax, %rax
  xor %r12, %r12
  mov $1, %r11
  cvtsi2sd %rax, %xmm0
.Lai1: movb (%rdi), %cl
  cmp $10, %cl
  je .Lai2
  test %cl, %cl
  jz .Lai2
  cmp $46, %cl
  jne .Lai3
  mov $1, %r12
  mov $1, %r11
  jmp .Lai_next
.Lai3: cmp $48, %cl
  jl .Lai2
  cmp $57, %cl
  jg .Lai2
  sub $48, %cl
  movzx %cl, %rcx
  cvtsi2sd %rcx, %xmm1
  test %r12, %r12
  jnz .Lai_frac
  mov $10, %rax
  cvtsi2sd %rax, %xmm2
  mulsd %xmm2, %xmm0
  addsd %xmm1, %xmm0
  jmp .Lai_next
.Lai_frac: imul $10, %r11
  cvtsi2sd %r11, %xmm2
  divsd %xmm2, %xmm1
  addsd %xmm1, %xmm0
.Lai_next: inc %rdi
  jmp .Lai1
.Lai2: movq %xmm0, %rax
  leave
  ret
pss_list_new:
  push %rbp
  mov %rsp, %rbp
  push %rdi
  imul $8, %rdi
  add $16, %rdi
  mov %rdi, %rsi
  call pss_malloc
  pop %rdi
  mov %rdi, (%rax)
  leave
  ret
pss_list_add:
  push %rbp
  mov %rsp, %rbp
  mov (%rdi), %rax
  mov %rsi, 16(%rdi, %rax, 8)
  incq (%rdi)
  leave
  ret
pss_list_remove:
  push %rbp
  mov %rsp, %rbp
  mov (%rdi), %rcx
  lea 16(%rdi, %rsi, 8), %rax
.Llr1: inc %rsi
  cmp %rsi, %rcx
  jle .Llr2
  mov 8(%rax), %rdx
  mov %rdx, (%rax)
  add $8, %rax
  jmp .Llr1
.Llr2: decq (%rdi)
  leave
  ret
