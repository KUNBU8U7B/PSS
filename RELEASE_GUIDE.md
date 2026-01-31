# PSS Release Guide

Ikuti langkah-langkah ini untuk merilis bahasa PSS Anda ke dunia!

## 1. Rilis di GitHub (Direkomendasikan)
GitHub adalah tempat terbaik agar orang bisa melihat kode sumber Anda.
- Buat repository baru di GitHub bernama `PSS`.
- Jalankan perintah ini di folder proyek Anda:
  ```bash
  git init
  git add .
  git commit -m "Initial release v1.0.0"
  git branch -M main
  git remote add origin https://github.com/username/PSS.git
  git push -u origin main
  ```
- Di halaman GitHub, klik **"Create a new release"** dan beri tag `v1.0.0`.

## 2. Rilis di PyPI (Agar bisa di-install via pip)
Jika Anda ingin orang bisa menginstall dengan `pip install pss-lang`:
- Buat akun di [PyPI](https://pypi.org/).
- Install tools untuk upload:
  ```bash
  pip install twine build
  ```
- Build paketnya:
  ```bash
  python -m build
  ```
- Upload ke PyPI:
  ```bash
  twine upload dist/*
  ```

## 3. Promosi
- Bagikan link GitHub Anda di LinkedIn, Twitter (X), atau forum pemrograman seperti Reddit r/programming.
- Buat video demo singkat yang menunjukkan PSS berjalan di Windows dan Android (Termux).

Selamat! Anda telah menciptakan bahasa pemrograman baru! 🚀
