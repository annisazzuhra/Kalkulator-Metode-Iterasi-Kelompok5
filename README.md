# Kalkulator-Metode-Iterasi-Kelompok5

Proyek UTS Komputasi Numerik A 

## A. Deskripsi Proyek
Aplikasi desktop berbasis antarmuka grafis (GUI) Python menggunakan pustaka `tkinter`. Program ini dirancang untuk mencari akar persamaan kuadrat F(x) = 0 menggunakan metode iterasi titik tetap (x = g(x)).
Seluruh parameter seperti persamaan, nilai awal (x0), toleransi galat, dan batas maksimum iterasi dimasukkan secara dinamis melalui kolom input aplikasi.

## B. Pembagian Tugas Anggota Kelompok
- Nabil Aulia Dika: Perancangan Antarmuka (GUI), Tabel Riwayat, Grafik, dan Integrasi Sistem
- Rafid Khaulika: Implementasi Mesin Hitung Cara 1 (Pendekatan Akar Kuadrat)
- Raisa Fahira: Implementasi Mesin Hitung Cara 2 (Pendekatan Pemindahan Suku x)
- Annisa Azzuhra Maghfirah: Implementasi Mesin Hitung Cara 3 (Pendekatan Pemfaktoran Aljabar)

## C. Tiga Cara Penyusunan Fungsi g(x)
Untuk bentuk umum persamaan kuadrat F(x) = a·x² + b·x + c = 0, fungsi iterasi g(x) dijabarkan melalui tiga cara berbeda.
Cara 1: g(x) = √((a·x² − F(x)) / a)
Cara 2: g(x) = x − F(x) / b
Cara 3: g(x) = −c / (a·x + b)

## D. Fitur Utama Program
- Input persamaan fleksibel (mendukung pangkat `^`, koma desimal, dan perkalian tersirat seperti `2x`).
- Deteksi otomatis koefisien a, b, dan c.
- Tabel riwayat iterasi lengkap dengan nilai xr, g(xr), F(g(xr)), dan galat.
- Visualisasi grafik galat berskala logaritmik dan kotak catatan proses otomatis.
- Validasi input untuk mencegah error saat kolom kosong atau salah format.

## E. Cara Menjalankan Program
1. Pastikan komputer sudah terinstal Python 3.
2. Simpan file `Kalkulator_Iterasi_Kelompok5.py` di dalam satu folder.
3. Buka terminal atau command prompt pada folder tersebut, lalu jalankan: python Kalkulator_Iterasi_Kelompok5.py
