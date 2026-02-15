# PSS v3.7.0 - Syntax Cheat Sheet (Python-Style)

PSS adalah bahasa pemrograman minimalis, cepat, dan berbasis indentasi. Berikut adalah panduan lengkap sintaksnya.

---

## 1. Struktur Dasar (Indentasi)
PSS menggunakan indentasi (spasi/tab) untuk menentukan blok kode. Jangan gunakan kata kunci `end`.
```python
func contoh();
    # Baris ini di dalam fungsi
    if true;
        # Baris ini di dalam if
        print "Halo"
    # Baris ini sudah di luar if
# Baris ini sudah di luar fungsi
```

---

## 2. Variabel & Tipe Data
PSS bersifat dinamis (tidak perlu deklarasi tipe).
- **Bilangan Bulat**: `x = 10`
- **Bilangan Desimal**: `y = 3.14`
- **Teks**: `pesan = "Halo Dunia"`
- **Boolean**: `status = true` atau `status = false`
- **Null**: `kosong = null`

---

## 3. Operator
- **Aritmatika**: `+`, `-`, `*`, `/`
- **Logika**: `and`, `or`, `not`
- **Perbandingan**: `==`, `>`, `<`, `!=`

---

## 4. Input Interaktif (Keyboard)
| Fungsi | Deskripsi |
|---|---|
| `input()` | Mengambil input umum (bisa teks/angka) |
| `int_input("msg")` | Mengambil angka bulat (Error jika diisi teks) |
| `float_input("msg")` | Mengambil angka desimal (Error jika diisi teks) |

*Contoh:*
```python
angka = int_input("Masukkan angka: ")
```

---

## 5. Output (Layar)
Gunakan `print`. Mendukung teks dan variabel.
```python
print "Hasilnya:", hasil
```

---

## 6. Percabangan (If-Elif-Else)
Gunakan titik koma `;` setelah header.
```python
if skor > 90;
    print "A"
elif skor > 70;
    print "B"
else;
    print "C"
```

---

## 7. Fungsi
Gunakan `func` dan `return`.
```python
func jumlah(a, b);
    return a + b

print jumlah(10, 5)
```

---

## 8. Validasi & Error
Jika Anda menggunakan `int_input()` atau `float_input()` dan memasukkan teks yang bukan angka, PSS akan otomatis berhenti dengan pesan:
`Error: Invalid Input`
