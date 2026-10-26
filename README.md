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

## F. Antarmuka (GUI) — Penjelasan Per Detail

Aplikasi ini dibuka dengan perintah pada bagian E. Jendelanya tersusun
dari atas ke bawah, masing-masing bagiannya punya ruang sendiri:

- **Navbar pil kaca (ala iOS).** Sebuah pil mengambang bersudut membulat
  penuh di atas jendela, berisi: Input, Tabel, Grafik, Catatan. Klik
  salah satunya untuk melompat langsung ke bagiannya.
- **Seksi 1 — Input & Cara Iterasi.** Tiga tombol cara: Cara 1
  (Diakarkan, Rafid), Cara 2 (Suku x Dipindah, Raisa), Cara 3
  (Difaktorkan, Annisa); rumus g(x) cara yang dipilih tampil di bawah
  tombol. Kolom masukan: Persamaan F(x) (contoh: x^2 - 2x - 3),
  Nilai awal (x0), Toleransi galat, dan Batas maksimum iterasi N
  (1-500). Tombol HITUNG menjalankan perhitungan (atau tekan Enter),
  tombol Contoh mengisi contoh, tombol Reset mengembalikan contoh dan
  mengosongkan semua hasil.
- **Spanduk hasil.** Setelah HITUNG, spanduk ini menyatakan: akar yang
  ditemukan, konvergen pada iterasi ke-berapa, cara yang dipakai,
  F(akar) sebagai bukti, dan galat akhir. Bila belum konvergen atau
  berhenti, spanduk menyatakan alasannya dan mengarahkan ke Catatan.
- **Seksi 2 — Tabel Iterasi.** Tabel besar (18 baris terlihat) dengan
  kolom: Iterasi, xr, g(xr), F(g(xr)), Galat. Baris hijau adalah
  iterasi saat konvergen tercapai.
- **Seksi 3 — Grafik Galat (Skala Log).** Grafik besar di bagiannya
  sendiri: kurva galat tiap iterasi dalam skala logaritma, lengkap
  dengan garis putus-putus oranye sebagai batas toleransi. Grafik
  menyentuh garis itu tepat saat konvergen.
- **Seksi 4 — Catatan Proses (Log Alur Kerja).** Panel ini adalah log
  alur kalkulator, langkah demi langkah, dari masukan sampai verifikasi
  hasil. Panel ini yang dibacakan saat presentasi (lihat bagian G).
- **Validasi sebelum run.** Huruf di kolom angka, nilai tak-hingga
  atau bukan angka, toleransi di luar 0 sampai 1, N di luar 1-500,
  |x0| di luar 1.000.000, dan persamaan kosong, tanpa x, konstan, atau
  tidak bisa dibaca — semuanya DITOLAK sebelum perhitungan berjalan,
  dengan pesan yang menyebut kolomnya. Jadi tidak ada lagi masukan
  sampah yang dibiarkan run lalu error di tengah jalan.
- **Jaminan tidak menimpa.** GUI hanya MENGIMPOR ketiga file mesin
  hitung (MetodeIterasi1/2/3.py); GUI tidak pernah menulis, menghapus,
  atau mengubah file lain. Satu-satunya file baru dari GUI adalah file
  GUI itu sendiri.

## G. Alur Presentasi — Naskah Baca

1. "Program ini mencari akar persamaan kuadrat F(x) = 0 dengan metode
   iterasi titik tetap: persamaan diubah menjadi x = g(x), lalu
   dihitung berulang x menjadi g(x) sampai galatnya lebih kecil dari
   toleransi."
2. "Ada tiga cara menyusun g(x), masing-masing dikerjakan satu anggota:
   Cara 1 mengakarkan, Cara 2 memindahkan suku x, Cara 3 memfaktorkan."
3. "Saya pilih caranya, isi persamaannya, nilai awalnya, toleransinya,
   dan batas iterasinya, lalu tekan HITUNG."
4. "Spanduk hasil menyatakan akarnya, konvergen pada iterasi
   ke-berapa, dan buktinya: F(akar) yang mendekati nol."
5. "Tabel ini merinci tiap iterasi: xr-nya, g(xr)-nya, F(g(xr))-nya,
   dan galatnya. Baris hijau adalah iterasi saat konvergen tercapai."
6. "Grafik ini memperlihatkan galat yang mengecil tiap iterasi dalam
   skala log; garis oranye adalah batas toleransi, dan grafik
   menyentuh garis itu saat konvergen."
7. "Terakhir, panel Catatan merangkum seluruh alur kerja dalam tujuh
   langkah: masukan diterima, persamaan dinormalkan, koefisien
   terdeteksi, cara dipilih, iterasi berjalan, pemeriksaan konvergensi,
   dan hasil beserta verifikasinya."
