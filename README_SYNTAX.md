# Dokumentasi Sintaks PSS v3.5.6 (Python-Style)

PSS v3.5.x memperkenalkan transformasi besar pada sintaksis: **Blok Berbasis Indentasi**. Anda tidak perlu lagi menggunakan kata kunci `end` untuk menutup fungsi atau percabangan.

---

## 1. Variabel & Tipe Data
PSS tetap menggunakan penentuan tipe data dinamis.
- **Integer**: `a = 10`
- **Float**: `b = 10.5`
- **Text**: `c = "Halo"`
- **Boolean**: `d = true`

---

## 2. Kontrol Alur (Berbasis Indentasi)
Akhir dari sebuah blok ditentukan oleh perubahan level indentasi (spasi/tab).

### Percabangan (If-Elif-Else)
```python
if a > b;
    print "a lebih besar"
elif a == b;
    print "sama"
else;
    print "b lebih besar"

# Kode di sini sudah di luar blok if
print "Selesai"
```

### Perulangan (While & For)
```python
while a > 0;
    print a
    a -= 1

for i in range(10);
    print i
```

---

## 3. Fungsi & Return Value
Fungsi didefinisikan dengan `func`. Hasil dapat dikembalikan menggunakan `return`.

```python
func tambah(a, b);
    return a + b

hasil = tambah(10, 5)
print hasil
```

---

## 4. Input Interaktif
PSS mendukung pengambilan data dari terminal secara langsung.

| Fungsi | Tipe Hasil | Contoh |
|--------|------------|--------|
| `input()` | Integer/Teks | `a = input()` |
| `input("msg")` | Integer/Teks | `b = input("Masukkan angka: ")` |
| `int_input()` | Integer | Sama dengan `input()` |
| `float_input()` | Float | Sama dengan `input()` |

---

## 5. Output (Print)
Gunakan `print` untuk menampilkan nilai. Argumen bisa dipisah dengan koma.

```python
print "Hasilnya adalah:", hasil
```

---

### Tips Penting
- **Indetasi Konsisten**: Pastikan menggunakan jumlah spasi/tab yang sama di dalam satu blok.
- **Titik Koma (optional)**: Header blok seperti `if` atau `func` tetap disarankan menggunakan `;` di akhir untuk kejelasan.
- **Tanpa `end`**: Jangan lagi menuliskan `end` karena akan dianggap sebagai perintah yang salah atau variabel tak dikenal.
