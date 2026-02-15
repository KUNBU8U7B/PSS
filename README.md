# PSS - Bahasa Pemrograman Performa Tinggi

## Versi 3.4.2 - Robust Edition

PSS adalah bahasa pemrograman yang dikompilasi langsung ke assembly x86_64, dirancang untuk performa maksimal dengan penggunaan memori minimal.

## Dokumentasi Lengkap
👉 **[Daftar Sintaks Lengkap & Penjelasan](file:///c:/Users/Pongo/Documents/CODING/PSS/README_SYNTAX.md)**

## Instalasi

### Instalasi Otomatis (Pertama Kali)
Cukup jalankan program PSS sekali:
```bash
./pss <file.pss>
```

PSS akan otomatis menginstal dirinya ke sistem (user-level di `/usr/local/bin` atau `~/.local/bin`).

Setelah itu, gunakan langsung dari mana saja:
```bash
pss <file.pss>
```

### Platform yang Didukung
- ✅ WSL (Windows Subsystem for Linux)
- ✅ Termux (Android)
- ✅ Ubuntu / Debian / Arch / Fedora
- ✅ Semua distribusi Linux dengan gcc

## Ringkasan Fitur v3.4.2
- **Operator Logika**: `and`, `or`, `not`
- **Blok Kontrol**: `if-elif-else`, `while`, `for range`, `func` (semua diakhiri `end`)
- **OOP Dasar**: `class`, `inherits`, `self`
- **Performa Ekstrim**: Penggunaan RAM < 1MB, Buffered I/O 512KB.

---
Open Source - Dikembangkan untuk pendidikan dan performa tinggi
