# Panduan Distribusi PSS ke GitHub & APT/PKG

Agar bahasa pemrograman PSS Anda bisa diinstal oleh orang lain di Linux atau Termux menggunakan perintah `apt` atau `pkg`, ikuti langkah-langkah berikut:

---

## 1. Unggah ke GitHub
1. Buat repositori baru di GitHub (misal: `nama-anda/pss`).
2. Di dalam folder `PSS` komputer Anda, jalankan:
   ```bash
   git init
   git add .
   git commit -m "Initial release v3.7.0"
   git remote add origin https://github.com/nama-anda/pss.git
   git push -u origin main
   ```

---

## 2. Cara Download "One-Line" (Paling Mudah)
Agar orang bisa menginstal dengan satu perintah (seperti `apt`), buatlah file `install.sh` di repositori Anda. Lalu orang lain cukup menjalankan:
```bash
curl -sSL https://raw.githubusercontent.com/nama-anda/pss/main/install.sh | bash
```

---

## 3. Membuat Paket `.deb` (Untuk `apt install`)
Jika ingin benar-benar bisa menggunakan `apt install`, Anda harus membuat paket Debian:

1. **Buat struktur folder paket**:
   ```bash
   mkdir -p pss_package/usr/local/bin
   mkdir -p pss_package/DEBIAN
   ```
2. **Copy file binary**:
   ```bash
   cp pss_native pss_package/usr/local/bin/
   cp pss pss_package/usr/local/bin/
   ```
3. **Buat file kontrol** (`pss_package/DEBIAN/control`):
   Isi dengan:
   ```text
   Package: pss
   Version: 3.7.0
   Section: utils
   Priority: optional
   Architecture: amd64
   Maintainer: Nama Anda <email@anda.com>
   Description: PSS Programming Language (Python-style)
   ```
4. **Bangun paket**:
   ```bash
   dpkg-deb --build pss_package pss_v3.7.0.deb
   ```
5. **Upload file `.deb`** tersebut ke bagian "Releases" di GitHub. Orang lain bisa mendownload dan menginstalnya dengan:
   ```bash
   sudo apt install ./pss_v3.7.0.deb
   ```

---

## 4. Tips Termux (`pkg install`)
Untuk Termux, Anda bisa mendaftarkan paket Anda ke **Termux User Repository (TUR)**, tetapi cara yang lebih lazim untuk proyek personal adalah menyediakan skrip instalasi otomatis yang mendeteksi lingkungan Termux dan melakukan `cp` ke `$PREFIX/bin`.

Saya sarankan gunakan metode **Skrip Instalasi Otomatis** karena paling kompatibel untuk Linux, WSL, dan Termux sekaligus.
