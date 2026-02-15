# Buku Panduan Sintaksis PSS (v3.8.0)
**Bahasa Pemrograman Berbasis Indentasi & Low-Level Optimization**

PSS adalah bahasa pemrograman yang dirancang untuk efisiensi tinggi, penggunaan memori minimal (< 2MB), dan kemudahan penulisan dengan gaya Python (Python-style indentation).

---

## I. Dasar-Dasar Bahasa

### 1. Komentar
Gunakan tanda pagar `#` untuk memberikan keterangan pada kode.
```python
# Ini adalah komentar, tidak akan dieksekusi oleh komputer
```

### 2. Variabel & Tipe Data
PSS tidak memerlukan deklarasi tipe data (Dynamic Typing). Variabel dibuat saat diberikan nilai.
- **Integer (Bilangan Bulat)**: `skor = 100`
- **Float (Bilangan Desimal)**: `ipk = 3.75`
- **Text (String)**: `nama = "Budi Santoso"`
- **Boolean**: `aktif = true`
- **Null (Kosong)**: `data = null`

---

## II. Struktur Blok & Indentasi
PSS menggunakan indentasi (spasi/tab) sebagai penanda blok kode.
> **Penting**: Tidak ada kata kunci `end` atau kurung kurawal `{}`. Akhir sebuah blok ditentukan oleh kembalinya baris ke level indentasi sebelumnya.

---

## III. Input & Output

### 1. Mencetak ke Layar (Print)
```python
print "Halo Guru!"
print "Nilai akhir:", nilai
```

### 2. Mengambil Masukan (Input) dengan Validasi Ketat
PSS v3.8.0 sangat aman. Jika input numerik diisi teks, program akan memberikan pesan error secara otomatis.

| Fungsi | Tipe Data | Deskripsi |
|---|---|---|
| `input()` | Umum | Mengambil masukan teks atau angka |
| `int_input("msg")` | Integer | Mengambil angka bulat (Aman/Strict) |
| `float_input("msg")` | Float | Mengambil angka desimal (Aman/Strict) |

---

## IV. Kontrol Alur Logika

### 1. Percabangan (If - Elif - Else)
Header harus diakhiri dengan titik koma `;`.
```python
if nilai > 85;
    print "Predikat: A"
elif nilai > 70;
    print "Predikat: B"
else;
    print "Predikat: C"
```

### 2. Perulangan (While Loop)
```python
angka = 5
while angka > 0;
    print "Hitung mundur:", angka
    angka = angka - 1
```

---

## V. Fungsi (Modularitas)
Fungsi memungkinkan kita membungkus logika agar bisa digunakan berulang kali. PSS mendukung **Local Scoping** (variabel di dalam fungsi terisolasi dari luar).

```python
func hitung_luas(panjang, lebar);
    luas = panjang * lebar
    return luas

hasil = hitung_luas(10, 5)
print "Luas Persegi:", hasil
```

---

## VI. Keunggulan Teknis untuk Guru
1. **Low-Level Control**: Setiap baris PSS dikonversi langsung menjadi bahasa assembly x86_64, memberikan pemahaman mendalam tentang cara kerja CPU.
2. **Extreme Memory Efficiency**: Berjalan lancar hanya dengan RAM kurang dari 2 megabyte.
3. **Safety First**: Fitur `Strict Numeric Validation` memastikan siswa belajar menangani input data yang benar sejak dini.
4. **Modern Syntax**: Mengajarkan kebersihan kode melalui aturan indentasi yang wajib.
