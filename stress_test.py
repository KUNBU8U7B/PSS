import os
import subprocess
import random

def generate_random_pss():
    ops = ['+', '-', '*', '/']
    comps = ['>', '<', '==', '!=']
    code = ""
    
    # 1. Assignments
    for i in range(3):
        code += f"v{i} = {random.randint(1, 100)}\n"
    
    # 2. Logic If
    code += "if v0 > 50;\n"
    code += "    print \"v0 besar\"\n"
    code += "else;\n"
    code += "    print \"v0 kecil\"\n"
    code += "end\n"
    
    # 3. Arithmetic Loop
    code += "i = 0\n"
    code += "while i < 10;\n"
    code += f"    v1 = v1 {random.choice(ops)} 1\n"
    code += "    i = i + 1\n"
    code += "end\n"
    code += "print \"Hasil akhir v1:\"\n"
    code += "print v1\n"
    
    return code

def main():
    os.makedirs("tests", exist_ok=True)
    success = 0
    total = 100
    
    print(f"Membangun Compiler Native dari pss.s...")
    subprocess.run(['wsl', 'gcc', 'pss.s', '-o', 'pss_native'], check=True)

    for i in range(total):
        filename = f"tests/test_{i}.pss"
        with open(filename, 'w') as f:
            f.write(generate_random_pss())
        
        try:
            # Run pss_native (Full Assembly Compiler) and redirect stdout to output.s
            with open('output.s', 'w') as out_f:
                result = subprocess.run(['wsl', './pss_native', filename], stdout=out_f, stderr=subprocess.PIPE, text=True, timeout=10)
            
            if result.returncode == 0:
                # Kompilasi output.s yang dihasilkan pss_native
                subprocess.run(['wsl', 'gcc', '-nostdlib', '-no-pie', 'output.s', '-o', 'final_out'], check=True)
                # Jalankan hasil akhir
                res_final = subprocess.run(['wsl', './final_out'], capture_output=True, text=True)
                success += 1
            else:
                print(f"Gagal di {filename}: {result.stderr}")
        except Exception as e:
            print(f"Error di {filename}: {str(e)}")
            
    print("------------------------------------------------")
    print(f"HASIL STRESS TEST: {success}/{total} LULUS")
    print("------------------------------------------------")

if __name__ == "__main__":
    main()
