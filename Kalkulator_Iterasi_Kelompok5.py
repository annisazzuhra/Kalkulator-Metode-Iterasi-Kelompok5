# -*- coding: utf-8 -*-
"""
KALKULATOR METODE ITERASI - KELOMPOK 5
Praktikum Komputasi Numerik A - Universitas Syiah Kuala

Antarmuka grafis (GUI) untuk tiga mesin hitung yang sudah ada di repo ini.
Mesin hitung TIDAK ditulis ulang di sini, melainkan diimpor dari file
masing-masing anggota:

  Cara 1 (Rafid)  : MetodeIterasi1.py - g(x) = sqrt((a*x^2 - F(x)) / a)
  Cara 2 (Raisa)  : MetodeIterasi2.py - g(x) = x - F(x) / b
  Cara 3 (Annisa) : MetodeIterasi3.py - g(x) = -c / (a*x + b)

File ini hanya berisi antarmuka: navbar kaca bentuk pil ala iOS + seksi
Input, Tabel, Grafik, dan Catatan. Semua perhitungan iterasi dikerjakan
oleh ketiga modul di atas. Masukan disaring dulu oleh
validasi_masukan(): huruf, NaN, tak-hingga, toleransi di luar (0, 1),
maks iterasi di luar 1-500, |x0| > 1e6, dan persamaan kosong/tanpa x/
konstan DITOLAK sebelum run, dengan pesan yang menyebut kolomnya.

Panel Catatan adalah LOG ALUR kerja kalkulator, langkah-demi-langkah
(Langkah 1-7), supaya bisa dibacakan saat presentasi: masukan diterima,
persamaan dinormalkan, koefisien terdeteksi, cara dipilih, iterasi
berjalan, pemeriksaan konvergensi, hasil & verifikasi F(akar).

Pembagian tugas (lihat README.md):
  Nabil Aulia Dika   : Perancangan Antarmuka (GUI), Tabel Riwayat,
                       Grafik, dan Integrasi Sistem
  Rafid Khaulika     : Mesin Hitung Cara 1
  Raisa Fahira       : Mesin Hitung Cara 2
  Annisa Azzuhra     : Mesin Hitung Cara 3

Cara menjalankan (dari folder yang berisi keempat file .py ini):
    python Kalkulator_Iterasi_Kelompok5.py

Hanya memakai pustaka standar Python (math, re, tkinter, io, contextlib).
"""

import contextlib
import io
import math
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Modul mesin hitung harus bisa diimpor walau program dijalankan dari
# folder lain: pastikan folder file ini sendiri ada di jalur impor.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import MetodeIterasi1 as mesin1
import MetodeIterasi2 as mesin2
import MetodeIterasi3 as mesin3

MESIN = {1: mesin1, 2: mesin2, 3: mesin3}
FUNGSI_CARA = {
    1: mesin1.kalkulator_cara1,
    2: mesin2.kalkulator_cara2,
    3: mesin3.kalkulator_cara3,
}

# =====================================================================
# ADAPTER - menghubungkan GUI ke mesin hitung anggota kelompok
# =====================================================================
#
# Ketiga mesin punya antarmuka yang sama:
#   kalkulator_caraN(persamaan_teks, x0, toleransi, max_iter)
#       -> (akar_atau_None, riwayat)
# dengan riwayat = list baris {iterasi, xr, g_xr, f_xr, galat}.
# Adapter ini menangkap cetakan console modul, menyimpulkan status dari
# galat terakhir, dan merapikan semuanya menjadi LOG ALUR langkah 1-7
# untuk panel Catatan.


def _koefisien_dan_kuadrat(teks_persamaan):
    """Info tampilan saja (bukan mesin hitung): a, b, c dan uji kuadrat.

    Dihitung lewat fungsi hitung_fx milik modul Cara 2 (parsernya paling
    lengkap: koma desimal, "=0", perkalian tersirat), semata untuk
    mengisi log alur. Iterasi tetap dikerjakan modul masing-masing.
    """
    rumus = mesin2.format_persamaan(teks_persamaan)
    f0, f1, fm1 = (mesin2.hitung_fx(t, rumus) for t in (0, 1, -1))
    c = f0
    a = (f1 + fm1) / 2 - c
    b = (f1 - fm1) / 2
    kuadrat = True
    for t in (0.0, 1.0, 2.5):
        try:
            hasil = (mesin2.hitung_fx(t + 3, rumus)
                     - 3 * mesin2.hitung_fx(t + 2, rumus)
                     + 3 * mesin2.hitung_fx(t + 1, rumus)
                     - mesin2.hitung_fx(t, rumus))
        except Exception:
            kuadrat = False
            break
        if abs(hasil) > 1e-6:
            kuadrat = False
            break
    return a, b, c, kuadrat


def _saring_pesan_modul(teks_cetakan):
    """Ambil hanya baris alasan/saran dari cetakan console modul.

    Baris tabel iterasi, pemisah "=====", judul kolom, dan baris hasil
    akhir dibuang: GUI sudah menampilkan tabelnya sendiri dan Langkah 7
    sudah menyatakan hasilnya — duplikasi hanya mengotori log alur.
    """
    kata_kunci = ("Berhenti", "tidak bisa", "tidak punya", "PERINGATAN",
                  "Penjelasan", "Saran")
    baris_bersih = []
    for baris in teks_cetakan.splitlines():
        baris = re.sub(r"\s+", " ", baris).strip()
        if not baris or set(baris) <= {"="}:
            continue
        if re.match(r"^\d+\s*\|", baris) or baris.startswith("Iterasi"):
            continue
        if any(k in baris for k in kata_kunci):
            baris_bersih.append(baris)
    return baris_bersih


RUMUS_CARA = {
    1: "g(x) = sqrt((a*x^2 - F(x)) / a)",
    2: "g(x) = x - F(x) / b",
    3: "g(x) = -c / (a*x + b)",
}


def hitung_dengan_modul(cara, teks_persamaan, x0, toleransi, max_iter):
    """Jalankan satu cara lewat modul anggota kelompok.

    Mengembalikan dict:
      status   : 'konvergen' | 'maks' | 'berhenti'
      akar     : nilai akar terakhir (None bila mesin tidak bisa jalan)
      riwayat  : list baris {iterasi, xr, g_xr, f_xr, galat}
      catatan  : LOG ALUR Langkah 1-7 untuk panel Catatan GUI
    """
    rumus = mesin2.format_persamaan(teks_persamaan)
    a, b, c, kuadrat = _koefisien_dan_kuadrat(teks_persamaan)
    catatan = [
        f"Langkah 1 \u2014 Masukan diterima: F(x) = {teks_persamaan}, "
        f"x0 = {x0:g}, toleransi = {toleransi:g}, "
        f"maks iterasi = {max_iter}.",
        f"Langkah 2 \u2014 Persamaan dinormalkan: {teks_persamaan} "
        f"-> {rumus}.",
        f"Langkah 3 \u2014 Koefisien terdeteksi: a = {a:g}, b = {b:g}, "
        f"c = {c:g}; " + ("persamaan kuadrat murni."
                          if kuadrat else
                          "peringatan: persamaan ini BUKAN kuadrat murni."),
        f"Langkah 4 \u2014 Cara {cara} dipilih: {RUMUS_CARA[cara]}.",
    ]

    penampung = io.StringIO()
    try:
        with contextlib.redirect_stdout(penampung):
            akar, riwayat = FUNGSI_CARA[cara](teks_persamaan, x0,
                                               toleransi, max_iter)
    except Exception as err:
        # Modul tidak bisa membaca/menjalankan masukan ini (misalnya
        # parser Cara 1 tidak mengenal koma desimal). Jendela tetap
        # hidup; alasannya tampil di log alur.
        catatan.append(f"Langkah 5 \u2014 Iterasi gagal dijalankan: "
                       f"mesin hitung Cara {cara} tidak dapat menjalankan "
                       f"masukan ini ({err}).")
        catatan.append("Saran: periksa format persamaan (contoh: "
                       "x^2 - 2x - 3) atau coba cara lain.")
        return {"status": "berhenti", "akar": None, "riwayat": [],
                "catatan": catatan}
    catatan.extend(_saring_pesan_modul(penampung.getvalue()))

    if riwayat:
        catatan.append(
            f"Langkah 5 \u2014 Iterasi berjalan: {len(riwayat)} iterasi "
            f"(rincian di tabel). Galat awal {riwayat[0]['galat']:.2e} "
            f"-> galat akhir {riwayat[-1]['galat']:.2e}.")
    else:
        catatan.append(
            "Langkah 5 \u2014 Iterasi tidak menghasilkan baris riwayat "
            "(mesin berhenti sebelum iterasi pertama).")

    if akar is None:
        catatan.append(
            "Langkah 6 \u2014 Pemeriksaan: mesin berhenti sebelum "
            "konvergen (alasan di atas).")
        if not any("Saran" in k for k in catatan):
            catatan.append("Saran: ganti nilai awal (x0) atau coba cara "
                           "lain.")
        catatan.append(
            "Langkah 7 \u2014 Hasil: tidak ada akar yang dihasilkan dari "
            "masukan ini.")
        return {"status": "berhenti", "akar": None, "riwayat": riwayat,
                "catatan": catatan}

    if riwayat and riwayat[-1]["galat"] < toleransi:
        n_iter = riwayat[-1]["iterasi"]
        f_akar = riwayat[-1]["f_xr"]
        catatan.append(
            f"Langkah 6 \u2014 Pemeriksaan konvergensi: galat akhir "
            f"{riwayat[-1]['galat']:.2e} < toleransi {toleransi:g} "
            f"-> KONVERGEN.")
        catatan.append(
            f"Langkah 7 \u2014 Hasil & verifikasi: akar \u2248 "
            f"{akar:.6f} pada iterasi ke-{n_iter}; F(akar) \u2248 "
            f"{f_akar:.2e} (mendekati nol, membuktikan akar).")
        return {"status": "konvergen", "akar": akar, "riwayat": riwayat,
                "catatan": catatan}

    catatan.append(
        f"Langkah 6 \u2014 Pemeriksaan konvergensi: batas maksimum "
        f"{max_iter} iterasi tercapai, belum konvergen.")
    if len(riwayat) >= 3 and riwayat[-2]["galat"] > 0:
        rasio = riwayat[-1]["galat"] / riwayat[-2]["galat"]
        if rasio >= 1:
            catatan.append(
                "Penjelasan: galat tidak mengecil, cara ini tidak akan "
                "konvergen dari nilai awal tersebut.")
        elif rasio > 0.9:
            catatan.append(
                "Penjelasan: galat mengecil tetapi sangat lambat.")
        else:
            catatan.append(
                "Penjelasan: galat sudah mengecil; naikkan batas "
                "maksimum iterasi agar tercapai.")
    if not any("Saran" in k for k in catatan):
        catatan.append("Saran: ganti nilai awal, naikkan maks iterasi, atau "
                       "perbesar toleransi.")
    try:
        f_pendekatan = mesin2.hitung_fx(akar, rumus)
        verifikasi = (f"; verifikasi F(pendekatan) \u2248 "
                      f"{f_pendekatan:.2e} (belum cukup kecil).")
    except Exception:
        verifikasi = "."
    catatan.append(
        f"Langkah 7 \u2014 Hasil sementara: pendekatan akar \u2248 "
        f"{akar:.6f}{verifikasi}")
    return {"status": "maks", "akar": akar, "riwayat": riwayat,
            "catatan": catatan}


# =====================================================================
# VALIDASI MASUKAN - dipanggil SEBELUM run, bisa dites tanpa jendela
# =====================================================================
#
# Prinsip: tidak ada masukan sampah yang lolos ke mesin lalu crash di
# tengah jalan. Setiap penolakan menyebut kolomnya dan nilai yang benar.


def _angka(teks, label, bilangan_bulat=False):
    """Baca satu kolom angka dengan penolakan yang spesifik."""
    t = teks.strip().replace(",", ".")
    if not t:
        raise ValueError(f"Kolom '{label}' kosong. Isi dulu dengan angka, "
                         f"contoh: 4.")
    if "_" in t:
        raise ValueError(f"Kolom '{label}' berisi '{teks.strip()}': gunakan "
                         f"angka biasa tanpa garis bawah.")
    try:
        nilai = int(t) if bilangan_bulat else float(t)
    except ValueError:
        jenis = "bilangan bulat" if bilangan_bulat else "angka"
        raise ValueError(f"Kolom '{label}' berisi '{teks.strip()}', bukan "
                         f"{jenis}. Perbaiki dulu, contoh: 4.")
    if not math.isfinite(nilai):
        raise ValueError(f"Kolom '{label}' berisi nilai tak-hingga/bukan "
                         f"angka ('{teks.strip()}'). Gunakan angka biasa, "
                         f"contoh: 4.")
    return nilai


def validasi_masukan(teks_persamaan, teks_x0, teks_tol, teks_maks):
    """Saring semua masukan sebelum run.

    Mengembalikan (x0, toleransi, maks_iter) bila semua sah, atau
    melempar ValueError dengan pesan per kolom bila ada yang tidak sah.
    """
    # --- persamaan ---
    pers = teks_persamaan.strip()
    if not pers:
        raise ValueError("Persamaan F(x) kosong. Isi dulu, contoh: "
                         "x^2 - 2x - 3.")
    rumus = mesin2.format_persamaan(pers)
    if not rumus or "x" not in rumus:
        raise ValueError(f"Persamaan '{pers}' tidak mengandung x. Tulis "
                         f"persamaan kuadrat, contoh: x^2 - 2x - 3.")
    try:
        f0 = mesin2.hitung_fx(0, rumus)
        f1 = mesin2.hitung_fx(1, rumus)
        f2 = mesin2.hitung_fx(2, rumus)
    except Exception:
        raise ValueError(f"Persamaan '{pers}' tidak bisa dibaca. Periksa "
                         f"penulisan (pangkat pakai ^, contoh: x^2 - 2x - 3).")
    if f0 == f1 == f2:
        raise ValueError(f"Persamaan '{pers}' konstan (nilainya tidak "
                         f"berubah terhadap x), jadi tidak punya akar "
                         f"untuk dicari. Tulis persamaan kuadrat, contoh: "
                         f"x^2 - 2x - 3.")

    # --- angka-angka ---
    x0 = _angka(teks_x0, "Nilai awal (x0)")
    if abs(x0) > 1e6:
        raise ValueError(f"Nilai awal (x0) = {x0:g} tidak masuk akal "
                         f"(di luar 1.000.000). Gunakan nilai awal yang "
                         f"dekat dengan akar, contoh: 4.")
    tol = _angka(teks_tol, "Toleransi galat")
    if not 0 < tol < 1:
        raise ValueError(f"Toleransi galat = {tol:g} tidak masuk akal. "
                         f"Toleransi harus di antara 0 dan 1, contoh: "
                         f"0.0001.")
    maks = _angka(teks_maks, "Batas maksimum iterasi", bilangan_bulat=True)
    if not 1 <= maks <= 500:
        raise ValueError(f"Batas maksimum iterasi = {maks} tidak masuk "
                         f"akal. Gunakan bilangan bulat 1-500, contoh: 50.")
    return x0, tol, maks


# =====================================================================
# BAGIAN 2 - ANTARMUKA (UI): navbar pil kaca + seksi vertikal
# =====================================================================
#
# Alur layar dari atas ke bawah, masing-masing bagiannya punya ruang
# sendiri yang lega (bukan dijejalkan berdampingan):
#   navbar -> Input & Cara -> spanduk hasil -> Tabel -> Grafik -> Catatan
# Item navbar menggulirkan layar ke bagiannya.
#
# Catatan jujur soal "kaca ala iOS": tkinter tidak punya blur kaca
# asli. Yang dipakai di sini adalah pendekatan yang aman: pil mengambang
# (sudut membulat penuh) warna navy muda + garis kilau di tepi atas +
# item navigasi berupa teks (bukan tombol kotak) supaya menyatu dengan
# pil. Fungsinya sama, tampilannya mendekati, tanpa trik rapuh.

WARNA = {
    "navy": "#14213d",
    "navy2": "#1e2f52",
    "pil": "#24365e",
    "pil_garis": "#4a5f8a",
    "pil_kilau": "#5b739e",
    "emas": "#f5b942",
    "emas_teks": "#14213d",
    "latar": "#f4f6fb",
    "putih": "#ffffff",
    "teks": "#1f2937",
    "teks_redup": "#64748b",
    "teks_panel": "#dbe4f5",
    "sukses_bg": "#e7f8f0", "sukses_fg": "#0c6b43",
    "waspada_bg": "#fdf3e3", "waspada_fg": "#92580a",
    "gagal_bg": "#fdecec", "gagal_fg": "#9c1c1c",
    "netral_bg": "#e8edf5", "netral_fg": "#475569",
    "akhir_bg": "#d9f2e3",
    "tol_fg": "#c2410c",
}

DESKRIPSI_CARA = {
    1: ("Cara 1 - Diakarkan (Rafid)",
        "g(x) = \u221a((a\u00b7x\u00b2 \u2212 F(x)) / a)\n"
        "Semua suku selain x\u00b2 dipindah ke ruas kanan, lalu kedua ruas "
        "diakarkan. Iterasi selalu menuju akar positif."),
    2: ("Cara 2 - Suku x Dipindah (Raisa)",
        "g(x) = x \u2212 F(x) / b\n"
        "Suku x dipindahkan ke ruas kiri, lalu dibagi koefisien x (b). "
        "Bentuk paling umum dari iterasi titik tetap."),
    3: ("Cara 3 - Difaktorkan (Annisa)",
        "g(x) = \u2212c / (a\u00b7x + b)\n"
        "Persamaan difaktorkan menjadi x(a\u00b7x + b) = \u2212c. Untuk "
        "x\u00b2\u22122x\u22123 bentuknya g(x) = 3 / (x \u2212 2)."),
}

CONTOH = {"persamaan": "x^2 - 2x - 3", "x0": "4", "tol": "0.0001",
          "maks": "50"}

TEKS_BANNER_AWAL = ("Hasil akan tampil di sini. Isi persamaan lalu tekan "
                    "HITUNG.")


def fmt_angka(v):
    """Format angka untuk tabel: 6 desimal, galat kecil dalam notasi e."""
    if v is None:
        return "-"
    if v != 0 and abs(v) < 1e-4:
        return f"{v:.3e}"
    return f"{v:.6f}"


def _pil_membulat(cv, x1, y1, x2, y2, r, **kwargs):
    """Gambar persegi bersudut membulat di canvas (pola arc + kotak)."""
    tag = kwargs.pop("tags", None)
    cv.create_rectangle(x1 + r, y1, x2 - r, y2, tags=tag, **kwargs)
    cv.create_rectangle(x1, y1 + r, x2, y2 - r, tags=tag, **kwargs)
    cv.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90,
                  style="pieslice", tags=tag, **kwargs)
    cv.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90,
                  style="pieslice", tags=tag, **kwargs)
    cv.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90,
                  style="pieslice", tags=tag, **kwargs)
    cv.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90,
                  style="pieslice", tags=tag, **kwargs)


class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Metode Iterasi - Kelompok 5")
        self.geometry("1160x860")
        self.minsize(1000, 700)
        self.configure(bg=WARNA["latar"])
        self.cara_terpilih = tk.IntVar(value=1)
        self._tol_terakhir = None
        self.bagian = {}
        self._bangun_gaya()
        self._bangun_navbar()
        self._bangun_area_gulir()
        self._bangun_seksi_input()
        self._bangun_spanduk()
        self._bangun_seksi_tabel()
        self._bangun_seksi_grafik()
        self._bangun_seksi_catatan()
        self._bangun_kaki()
        self.pilih_cara(1)
        self.isi_contoh()
        self.bind("<Return>", lambda _e: self.hitung())

    # ---------- gaya dasar ----------
    def _bangun_gaya(self):
        gaya = ttk.Style(self)
        gaya.theme_use("clam")
        gaya.configure("Tabel.Treeview",
                       background=WARNA["putih"],
                       fieldbackground=WARNA["putih"],
                       foreground=WARNA["teks"],
                       rowheight=26,
                       font=("Consolas", 11))
        gaya.configure("Tabel.Treeview.Heading",
                       background=WARNA["navy"],
                       foreground=WARNA["putih"],
                       font=("Segoe UI", 11, "bold"),
                       padding=(6, 8))
        gaya.map("Tabel.Treeview",
                 background=[("selected", "#fde9bd")],
                 foreground=[("selected", WARNA["teks"])])

    # ---------- navbar pil kaca ----------
    def _bangun_navbar(self):
        self._nav = tk.Canvas(self, height=64, bg=WARNA["latar"],
                              highlightthickness=0)
        self._nav.pack(side="top", fill="x", padx=18, pady=(14, 2))
        self._nav.bind("<Configure>", lambda _e: self._gambar_navbar())

    def _gambar_navbar(self):
        cv = self._nav
        cv.delete("nav")
        lebar = max(cv.winfo_width(), 400)
        # Pil mengambang: tidak selebar layar penuh, ada margin di semua
        # sisi sehingga tampak melayang di atas latar.
        _pil_membulat(cv, 4, 4, lebar - 4, 60, 28, fill=WARNA["pil"],
                       outline=WARNA["pil_garis"], width=1, tags="nav")
        # Garis kilau di tepi atas pil (efek kaca).
        cv.create_line(32, 6, lebar - 32, 6, fill=WARNA["pil_kilau"],
                       width=1, tags="nav")
        cv.create_text(28, 24, anchor="w",
                       text="KALKULATOR METODE ITERASI",
                       fill=WARNA["emas"], font=("Segoe UI", 13, "bold"),
                       tags="nav")
        cv.create_text(28, 44, anchor="w",
                       text="Kelompok 5 \u00b7 Komputasi Numerik A",
                       fill=WARNA["teks_panel"], font=("Segoe UI", 9),
                       tags="nav")
        # Item navigasi sebagai teks (menyatu dengan pil, bukan tombol
        # kotak): klik menggulir, hover berubah emas.
        x = lebar - 28
        for kunci, label in (("catatan", "Catatan"), ("grafik", "Grafik"),
                             ("tabel", "Tabel"), ("input", "Input")):
            item = cv.create_text(x, 32, anchor="e", text=label,
                                  fill=WARNA["putih"],
                                  font=("Segoe UI", 11, "bold"), tags="nav")
            cv.tag_bind(item, "<Button-1>",
                        lambda _e, k=kunci: self._gulir_ke(k))
            cv.tag_bind(item, "<Enter>", lambda _e, i=item: cv.itemconfig(
                i, fill=WARNA["emas"]))
            cv.tag_bind(item, "<Leave>", lambda _e, i=item: cv.itemconfig(
                i, fill=WARNA["putih"]))
            kotak = cv.bbox(item)
            x = kotak[0] - 18

    def _gulir_ke(self, kunci):
        """Gulirkan area ke seksi yang diminta lewat navbar."""
        frame = self.bagian.get(kunci)
        if frame is None:
            return
        self._dalam.update_idletasks()
        kotak = self._kanvas.bbox("all")
        if not kotak or kotak[3] <= 0:
            return
        self._kanvas.yview_moveto(frame.winfo_y() / kotak[3])

    # ---------- area gulir ----------
    def _bangun_area_gulir(self):
        luar = tk.Frame(self, bg=WARNA["latar"])
        luar.pack(side="top", fill="both", expand=True)
        self._kanvas = tk.Canvas(luar, bg=WARNA["latar"],
                                 highlightthickness=0)
        scroll = ttk.Scrollbar(luar, orient="vertical",
                               command=self._kanvas.yview)
        self._kanvas.configure(yscrollcommand=scroll.set)
        self._kanvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._dalam = tk.Frame(self._kanvas, bg=WARNA["latar"])
        self._kanvas.create_window((0, 0), window=self._dalam, anchor="nw")
        self._dalam.bind("<Configure>", lambda _e: self._kanvas.configure(
            scrollregion=self._kanvas.bbox("all")))
        self._kanvas.bind("<MouseWheel>", lambda e: self._kanvas.yview_scroll(
            -1 if e.delta > 0 else 1, "units"))
        self._kanvas.bind("<Button-4>", lambda _e: self._kanvas.yview_scroll(
            -1, "units"))
        self._kanvas.bind("<Button-5>", lambda _e: self._kanvas.yview_scroll(
            1, "units"))

    def _judul_seksi(self, teks):
        tk.Label(self._dalam, text=teks, bg=WARNA["latar"],
                 fg=WARNA["navy"], font=("Segoe UI", 13, "bold"),
                 anchor="w").pack(fill="x", padx=18, pady=(16, 6))

    # ---------- seksi input ----------
    def _bangun_seksi_input(self):
        self._judul_seksi("1 \u00b7 Input & Cara Iterasi")
        kartu = tk.Frame(self._dalam, bg=WARNA["putih"],
                         highlightthickness=1,
                         highlightbackground="#d5dce8")
        kartu.pack(fill="x", padx=18, pady=(0, 4))
        self.bagian["input"] = kartu

        tk.Label(kartu, text="PILIH CARA", bg=WARNA["putih"],
                 fg=WARNA["teks_redup"], font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        baris_cara = tk.Frame(kartu, bg=WARNA["putih"])
        baris_cara.pack(fill="x", padx=16)
        self.tombol_cara = {}
        for n in (1, 2, 3):
            judul, _ = DESKRIPSI_CARA[n]
            b = tk.Button(baris_cara, text=judul, anchor="w",
                          font=("Segoe UI", 10, "bold"),
                          bg=WARNA["navy2"], fg=WARNA["putih"],
                          activebackground=WARNA["emas"],
                          activeforeground=WARNA["emas_teks"],
                          relief="flat", bd=0, padx=14, pady=9,
                          cursor="hand2",
                          command=lambda k=n: self.pilih_cara(k))
            b.pack(side="left", padx=(0, 8))
            self.tombol_cara[n] = b
        self.lbl_deskripsi = tk.Label(
            kartu, text="", bg=WARNA["putih"], fg=WARNA["teks"],
            font=("Segoe UI", 10), anchor="w", justify="left",
            wraplength=1060)
        self.lbl_deskripsi.pack(fill="x", padx=16, pady=(8, 4))

        self.entri = {}
        tk.Label(kartu, text="Persamaan F(x)", bg=WARNA["putih"],
                 fg=WARNA["teks_redup"], font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(8, 2))
        e = tk.Entry(kartu, font=("Consolas", 13), bg="#f8fafc",
                     fg=WARNA["teks"], relief="solid", bd=1,
                     insertbackground=WARNA["teks"])
        e.pack(fill="x", padx=16, ipady=5)
        self.entri["persamaan"] = e

        grid = tk.Frame(kartu, bg=WARNA["putih"])
        grid.pack(fill="x", padx=16, pady=(10, 4))
        for kolom in range(3):
            grid.columnconfigure(kolom, weight=1)
        for kolom, (kunci, label) in enumerate((
            ("x0", "Nilai awal (x0)"),
            ("tol", "Toleransi galat"),
            ("maks", "Batas maksimum iterasi (N, 1-500)"),
        )):
            tk.Label(grid, text=label, bg=WARNA["putih"],
                     fg=WARNA["teks_redup"], font=("Segoe UI", 9, "bold"),
                     anchor="w").grid(row=0, column=kolom, sticky="w",
                                      padx=(0, 12))
            ent = tk.Entry(grid, font=("Consolas", 12), bg="#f8fafc",
                           fg=WARNA["teks"], relief="solid", bd=1,
                           insertbackground=WARNA["teks"])
            ent.grid(row=1, column=kolom, sticky="ew", padx=(0, 12),
                     ipady=5)
            self.entri[kunci] = ent

        btn = tk.Frame(kartu, bg=WARNA["putih"])
        btn.pack(fill="x", padx=16, pady=(12, 14))
        tk.Button(btn, text="HITUNG", command=self.hitung,
                  font=("Segoe UI", 12, "bold"),
                  bg=WARNA["emas"], fg=WARNA["emas_teks"],
                  activebackground="#ffc95e",
                  activeforeground=WARNA["emas_teks"],
                  relief="flat", bd=0, padx=26, pady=10,
                  cursor="hand2").pack(side="left")
        tk.Button(btn, text="Contoh", command=self.isi_contoh,
                  font=("Segoe UI", 11),
                  bg=WARNA["navy2"], fg=WARNA["putih"],
                  activebackground=WARNA["navy2"],
                  activeforeground=WARNA["emas"],
                  relief="flat", bd=0, padx=18, pady=10,
                  cursor="hand2").pack(side="left", padx=(10, 0))
        tk.Button(btn, text="Reset", command=self._reset,
                  font=("Segoe UI", 11),
                  bg="#e8edf5", fg=WARNA["teks"],
                  activebackground="#d5dce8",
                  activeforeground=WARNA["teks"],
                  relief="flat", bd=0, padx=18, pady=10,
                  cursor="hand2").pack(side="left", padx=(10, 0))
        tk.Label(btn, text="Reset mengembalikan contoh dan mengosongkan "
                            "hasil.",
                 bg=WARNA["putih"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(14, 0))

    # ---------- spanduk hasil ----------
    def _bangun_spanduk(self):
        self.lbl_hasil = tk.Label(
            self._dalam, text=TEKS_BANNER_AWAL,
            bg=WARNA["netral_bg"], fg=WARNA["netral_fg"],
            font=("Segoe UI", 12, "bold"), anchor="w",
            padx=16, pady=12, wraplength=1080, justify="left")
        self.lbl_hasil.pack(fill="x", padx=18, pady=(14, 0))

    # ---------- seksi tabel ----------
    def _bangun_seksi_tabel(self):
        self._judul_seksi("2 \u00b7 Tabel Iterasi")
        bingkai = tk.Frame(self._dalam, bg=WARNA["latar"])
        bingkai.pack(fill="x", padx=18)
        self.bagian["tabel"] = bingkai
        kolom = ("iterasi", "xr", "g_xr", "f_xr", "galat")
        self.tabel = ttk.Treeview(bingkai, columns=kolom, height=18,
                                  show="headings", style="Tabel.Treeview")
        for kunci, judul, lebar in (
            ("iterasi", "Iterasi", 90),
            ("xr", "xr", 180),
            ("g_xr", "g(xr)", 180),
            ("f_xr", "F(g(xr))", 180),
            ("galat", "Galat", 180),
        ):
            self.tabel.heading(kunci, text=judul)
            self.tabel.column(kunci, width=lebar, anchor="center",
                              stretch=True)
        self.tabel.tag_configure("ganjil", background="#eef2f9")
        self.tabel.tag_configure("akhir", background=WARNA["akhir_bg"])
        scroll = ttk.Scrollbar(bingkai, orient="vertical",
                               command=self.tabel.yview)
        self.tabel.configure(yscrollcommand=scroll.set)
        self.tabel.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        tk.Label(self._dalam,
                 text="Baris hijau = iterasi saat konvergen tercapai.",
                 bg=WARNA["latar"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9), anchor="w").pack(
                     fill="x", padx=18, pady=(4, 0))

    # ---------- seksi grafik ----------
    def _bangun_seksi_grafik(self):
        self._judul_seksi("3 \u00b7 Grafik Galat (Skala Log)")
        bingkai = tk.Frame(self._dalam, bg=WARNA["latar"])
        bingkai.pack(fill="x", padx=18)
        self.bagian["grafik"] = bingkai
        self.kanvas = tk.Canvas(bingkai, width=1020, height=360,
                                bg=WARNA["putih"], highlightthickness=1,
                                highlightbackground="#d5dce8")
        self.kanvas.pack(fill="x", expand=True)
        tk.Label(self._dalam,
                 text="Garis putus-putus oranye = batas toleransi. "
                      "Grafik menyentuh garis itu saat konvergen.",
                 bg=WARNA["latar"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9), anchor="w").pack(
                     fill="x", padx=18, pady=(4, 0))

    # ---------- seksi catatan (log alur) ----------
    def _bangun_seksi_catatan(self):
        self._judul_seksi("4 \u00b7 Catatan Proses (Log Alur Kerja)")
        bingkai = tk.Frame(self._dalam, bg=WARNA["latar"])
        bingkai.pack(fill="x", padx=18)
        self.bagian["catatan"] = bingkai
        tk.Label(bingkai,
                 text="Panel ini adalah log alur kalkulator, langkah demi "
                      "langkah, untuk dibacakan saat presentasi.",
                 bg=WARNA["latar"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(0, 4))
        self.txt_catatan = tk.Text(
            bingkai, height=10, font=("Consolas", 10),
            bg="#111827", fg="#d7dee9", relief="flat",
            padx=12, pady=10, wrap="word", state="disabled")
        self.txt_catatan.pack(fill="x", expand=True)

    def _bangun_kaki(self):
        tk.Label(self._dalam,
                 text="Kelompok 5 \u00b7 Komputasi Numerik A \u00b7 "
                      "UI: Nabil Aulia Dika \u00b7 Mesin: Rafid (Cara 1), "
                      "Raisa (Cara 2), Annisa (Cara 3)",
                 bg=WARNA["latar"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9), anchor="w").pack(
                     fill="x", padx=18, pady=(16, 20))

    # ---------- interaksi ----------
    def pilih_cara(self, n):
        self.cara_terpilih.set(n)
        for k, b in self.tombol_cara.items():
            if k == n:
                b.configure(bg=WARNA["emas"], fg=WARNA["emas_teks"])
            else:
                b.configure(bg=WARNA["navy2"], fg=WARNA["putih"])
        self.lbl_deskripsi.configure(text=DESKRIPSI_CARA[n][1])

    def isi_contoh(self):
        for kunci, nilai in CONTOH.items():
            e = self.entri[kunci]
            e.delete(0, "end")
            e.insert(0, nilai)

    def _reset(self):
        """Kembalikan contoh dan kosongkan semua hasil."""
        self.isi_contoh()
        self.pilih_cara(1)
        self._tol_terakhir = None
        for baris_id in self.tabel.get_children():
            self.tabel.delete(baris_id)
        self.lbl_hasil.configure(text=TEKS_BANNER_AWAL,
                                 bg=WARNA["netral_bg"],
                                 fg=WARNA["netral_fg"])
        self._tulis_catatan([])
        self._gambar_grafik([])

    def _tulis_catatan(self, baris_baris):
        self.txt_catatan.configure(state="normal")
        self.txt_catatan.delete("1.0", "end")
        for b in baris_baris:
            self.txt_catatan.insert("end", "\u2022 " + b + "\n")
        self.txt_catatan.configure(state="disabled")

    def _gambar_grafik(self, riwayat):
        cv = self.kanvas
        cv.delete("all")
        self.update_idletasks()
        lebar = max(cv.winfo_width(), 900)
        tinggi = max(cv.winfo_height(), 320)
        if not riwayat:
            cv.create_text(lebar / 2, tinggi / 2,
                           text="Belum ada data iterasi",
                           fill=WARNA["teks_redup"],
                           font=("Segoe UI", 10))
            return
        galat = [max(r["galat"], 1e-16) for r in riwayat]
        log_g = [math.log10(v) for v in galat]
        lo, hi = min(log_g), max(log_g)
        tol = self._tol_terakhir
        log_tol = math.log10(tol) if tol else None
        if log_tol is not None:
            lo, hi = min(lo, log_tol), max(hi, log_tol)
        if hi - lo < 1e-9:
            hi = lo + 1
        pad_k, pad_a, pad_b = 44, 12, 22
        titik = []
        for i, lg in enumerate(log_g):
            x = pad_k + (lebar - pad_k - 10) * (
                i / max(len(log_g) - 1, 1))
            y = pad_a + (tinggi - pad_a - pad_b) * (hi - lg) / (hi - lo)
            titik.append((x, y))
        for frac in (0, 0.5, 1):
            y = pad_a + (tinggi - pad_a - pad_b) * frac
            cv.create_line(pad_k, y, lebar - 10, y, fill="#e5eaf2")
        cv.create_text(4, pad_a + 2, anchor="nw",
                       text=f"1e{hi:.0f}", fill=WARNA["teks_redup"],
                       font=("Consolas", 8))
        cv.create_text(4, tinggi - pad_b - 10, anchor="nw",
                       text=f"1e{lo:.0f}", fill=WARNA["teks_redup"],
                       font=("Consolas", 8))
        if log_tol is not None:
            y_tol = pad_a + (tinggi - pad_a - pad_b) * (hi - log_tol) / (
                hi - lo)
            cv.create_line(pad_k, y_tol, lebar - 10, y_tol,
                           fill=WARNA["tol_fg"], dash=(6, 4), width=2)
            cv.create_text(lebar - 12, y_tol - 14, anchor="ne",
                           text="toleransi", fill=WARNA["tol_fg"],
                           font=("Segoe UI", 8, "bold"))
        if len(titik) > 1:
            cv.create_line(*[c for p in titik for c in p],
                           fill="#2563eb", width=2, smooth=True)
        for (x, y) in titik:
            cv.create_oval(x - 4, y - 4, x + 4, y + 4,
                           fill=WARNA["emas"], outline="#b97f10")

    def hitung(self):
        # 1. Saring masukan dulu — sampah tidak boleh sampai ke mesin.
        teks_pers = self.entri["persamaan"].get().strip()
        try:
            x0, tol, maks = validasi_masukan(
                teks_pers, self.entri["x0"].get(),
                self.entri["tol"].get(), self.entri["maks"].get())
        except ValueError as err:
            messagebox.showerror("Masukan tidak sah", str(err))
            return
        self._tol_terakhir = tol

        # 2. Jalankan cara yang dipilih lewat modul anggota kelompok
        cara = self.cara_terpilih.get()
        hasil = hitung_dengan_modul(cara, teks_pers, x0, tol, maks)

        # 3. Isi tabel (baris terakhir = baris konvergen, disorot hijau)
        for baris_id in self.tabel.get_children():
            self.tabel.delete(baris_id)
        n_baris = len(hasil["riwayat"])
        for idx, r in enumerate(hasil["riwayat"]):
            tag = []
            if idx % 2:
                tag.append("ganjil")
            if idx == n_baris - 1 and hasil["status"] == "konvergen":
                tag.append("akhir")
            self.tabel.insert(
                "", "end",
                values=(r["iterasi"], fmt_angka(r["xr"]),
                        fmt_angka(r["g_xr"]), fmt_angka(r["f_xr"]),
                        fmt_angka(r["galat"])),
                tags=tuple(tag))

        # 4. Spanduk hasil — lengkap dengan bukti F(akar) & galat akhir
        status = hasil["status"]
        akar = hasil["akar"]
        if status == "konvergen":
            n_iter = hasil["riwayat"][-1]["iterasi"]
            f_akar = hasil["riwayat"][-1]["f_xr"]
            galat = hasil["riwayat"][-1]["galat"]
            teks = (f"\u2713  Akar \u2248 {akar:.6f}   \u00b7   konvergen "
                    f"pada iterasi ke-{n_iter}   \u00b7   Cara {cara}   "
                    f"\u00b7   F(akar) \u2248 {f_akar:.2e}   \u00b7   "
                    f"galat akhir {galat:.2e}")
            bg, fg = WARNA["sukses_bg"], WARNA["sukses_fg"]
        elif status == "maks":
            teks = (f"Akar pendekatan \u2248 {akar:.6f} - belum konvergen "
                    f"dalam {maks} iterasi (Cara {cara}). Lihat log alur "
                    f"di Catatan untuk analisis galatnya.")
            bg, fg = WARNA["waspada_bg"], WARNA["waspada_fg"]
        else:
            teks = (f"Iterasi berhenti sebelum konvergen (Cara {cara}) - "
                    "lihat log alur di Catatan.")
            bg, fg = WARNA["gagal_bg"], WARNA["gagal_fg"]
        self.lbl_hasil.configure(text=teks, bg=bg, fg=fg)

        # 5. Log alur & grafik
        self._tulis_catatan(hasil["catatan"])
        self._gambar_grafik(hasil["riwayat"])


if __name__ == "__main__":
    Aplikasi().mainloop()
