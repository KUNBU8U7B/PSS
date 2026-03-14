
import sys

with open('pss_core.c', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Remove # comments that are inside string literals for emit()
    if 'emit("' in line and '#' in line:
        # Simple removal: find the first # and truncate if it looks like a python comment
        # but be careful not to remove # in assembly like [sp, #-16]!
        # Actually, in the error logs: "  fcvtns x0, d0\n" # ARM64 implementation simplified for now
        # The # is outside the C string literal or inside the macro call.
        idx = line.find(' # ')
        if idx != -1:
            # Check if it's followed by a comment-like string
            line = line[:idx] + ");\n"
        elif ' # ' in line or ' #.' in line or ' # r' in line:
            # More aggressive for known bad patterns
             line = line.split(' #')[0] + ");\n"
             
    # Specifically for the ARM64 part that caused the last error
    if '"  fcvtns x0, d0\\n" #' in line:
        line = line.split(' #')[0] + ");\n"
    
    new_lines.append(line)

# Also fix the comparison logic which was suspect
content = "".join(new_lines)

# Ensure the comparison uses ucomisd
if 'ucomisd' not in content:
    old_cmp = '      emit("  cmp %%rbx, %%rax\\n");'
    new_cmp = '      emit("  movq %%rax, %%xmm0\\n  movq %%rbx, %%xmm1\\n  ucomisd %%xmm1, %%xmm0\\n");'
    content = content.replace(old_cmp, new_cmp)
    
    # Fix the flags for unsigned/float comparison
    content = content.replace('emit("  setl %%al\\n");', 'emit("  setb %%al\\n");')
    content = content.replace('emit("  setle %%al\\n");', 'emit("  setbe %%al\\n");')
    content = content.replace('emit("  setg %%al\\n");', 'emit("  seta %%al\\n");')
    content = content.replace('emit("  setae %%al\\n");', 'emit("  setae %%al\\n");') # Already correct or was setge

with open('pss_core.c', 'w', encoding='utf-8') as f:
    f.write(content)

print("Final Fix V4 applied.")
