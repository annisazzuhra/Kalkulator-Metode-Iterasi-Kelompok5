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

File ini hanya berisi antarmuka: kolom masukan, pilihan cara, tabel
riwayat iterasi, grafik galat skala log, dan catatan proses. Semua
perhitungan iterasi dikerjakan oleh ketiga modul di atas.

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
# Bedanya dengan mesin terpadu dulu: tidak ada status konvergen di
# return value, dan pesan proses dicetak ke console, bukan dikembalikan.
# Adapter ini menangkap cetakan itu, menyimpulkan status dari galat
# terakhir, dan merapikan semuanya menjadi satu dict untuk GUI.


def _koefisien_dan_kuadrat(teks_persamaan):
    """Info tampilan saja (bukan mesin hitung): a, b, c dan uji kuadrat.

    Dihitung lewat fungsi hitung_fx milik modul Cara 2 (parsernya paling
    lengkap: koma desimal, "=0", perkalian tersirat), semata untuk
    mengisi panel catatan. Iterasi tetap dikerjakan modul masing-masing.
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

    Baris tabel iterasi, pemisah "=====", dan judul kolom dibuang karena
    GUI sudah menampilkan tabelnya sendiri.
    """
    kata_kunci = ("Berhenti", "tidak bisa", "tidak punya", "PERINGATAN",
                  "Penjelasan", "Saran", "Hasil Akhir", "mencapai batas",
                  "Sudah mencapai", "tidak akan konvergen", "sangat pelan",
                  "naikkan batas")
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
      catatan  : list kalimat penjelasan untuk panel catatan GUI
    """
    a, b, c, kuadrat = _koefisien_dan_kuadrat(teks_persamaan)
    catatan = [
        f"Koefisien terdeteksi: a = {a:g}, b = {b:g}, c = {c:g}.",
        "Persamaan terdeteksi kuadrat murni."
        if kuadrat else
        "Peringatan: persamaan ini BUKAN kuadrat murni.",
        f"Rumus iterasi Cara {cara}: {RUMUS_CARA[cara]}.",
    ]

    penampung = io.StringIO()
    try:
        with contextlib.redirect_stdout(penampung):
            akar, riwayat = FUNGSI_CARA[cara](teks_persamaan, x0,
                                               toleransi, max_iter)
    except Exception as err:
        # Modul tidak bisa membaca/menjalankan masukan ini (misalnya
        # parser Cara 1 tidak mengenal koma desimal yang lolos saringan
        # awal). Jendela tetap hidup; alasannya tampil di catatan.
        catatan.append(f"Mesin hitung Cara {cara} tidak dapat menjalankan "
                       f"masukan ini: {err}.")
        catatan.append("Saran: periksa format persamaan (contoh: "
                       "x^2 - 2x - 3) atau coba cara lain.")
        return {"status": "berhenti", "akar": None, "riwayat": [],
                "catatan": catatan}
    catatan.extend(_saring_pesan_modul(penampung.getvalue()))

    if akar is None:
        status = "berhenti"
        if not any("Berhenti" in k or "tidak" in k for k in catatan[3:]):
            catatan.append("Mesin hitung tidak menghasilkan akar untuk "
                           "masukan ini.")
        if not any("Saran" in k for k in catatan[3:]):
            catatan.append("Saran: ganti nilai awal (x0) atau coba cara "
                           "lain.")
    elif riwayat and riwayat[-1]["galat"] < toleransi:
        status = "konvergen"
        n_iter = riwayat[-1]["iterasi"]
        catatan.append(
            f"Konvergen pada iterasi ke-{n_iter}: galat "
            f"{riwayat[-1]['galat']:.2e} sudah di bawah toleransi "
            f"{toleransi:g}.")
    else:
        status = "maks"
        catatan.append(
            f"Batas maksimum {max_iter} iterasi tercapai, belum konvergen.")
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
        catatan.append("Saran: ganti nilai awal, naikkan maks iterasi, atau "
                       "perbesar toleransi.")

    return {"status": status, "akar": akar, "riwayat": riwayat,
            "catatan": catatan}


# =====================================================================
# BAGIAN 2 - ANTARMUKA (UI)
# =====================================================================

WARNA = {
    "navy": "#14213d",        # panel kiri
    "navy2": "#1e2f52",       # kartu cara (belum dipilih)
    "navy3": "#0e1830",       # judul di panel kiri
    "emas": "#f5b942",        # aksen / tombol utama
    "emas_teks": "#14213d",
    "latar": "#f4f6fb",       # latar panel kanan
    "putih": "#ffffff",
    "teks": "#1f2937",
    "teks_redup": "#64748b",
    "teks_panel": "#dbe4f5",
    "sukses_bg": "#e7f8f0", "sukses_fg": "#0c6b43",
    "waspada_bg": "#fdf3e3", "waspada_fg": "#92580a",
    "gagal_bg": "#fdecec", "gagal_fg": "#9c1c1c",
    "netral_bg": "#e8edf5", "netral_fg": "#475569",
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


def fmt_angka(v):
    """Format angka untuk tabel: 6 desimal, galat kecil dalam notasi e."""
    if v is None:
        return "-"
    if v != 0 and abs(v) < 1e-4:
        return f"{v:.3e}"
    return f"{v:.6f}"


class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Metode Iterasi - Kelompok 5")
        self.geometry("1160x740")
        self.minsize(1020, 660)
        self.configure(bg=WARNA["latar"])
        self.cara_terpilih = tk.IntVar(value=1)
        self._bangun_gaya()
        self._bangun_panel_kiri()
        self._bangun_panel_kanan()
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
                       rowheight=25,
                       font=("Consolas", 10))
        gaya.configure("Tabel.Treeview.Heading",
                       background=WARNA["navy"],
                       foreground=WARNA["putih"],
                       font=("Segoe UI", 10, "bold"),
                       padding=(6, 6))
        gaya.map("Tabel.Treeview",
                 background=[("selected", "#fde9bd")],
                 foreground=[("selected", WARNA["teks"])])

    # ---------- panel kiri ----------
    def _bangun_panel_kiri(self):
        kiri = tk.Frame(self, bg=WARNA["navy"], width=330)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)

        tk.Label(kiri, text="KALKULATOR", bg=WARNA["navy"],
                 fg=WARNA["emas"], font=("Segoe UI", 11, "bold"),
                 anchor="w").pack(fill="x", padx=22, pady=(14, 0))
        tk.Label(kiri, text="Metode Iterasi", bg=WARNA["navy"],
                 fg=WARNA["putih"], font=("Segoe UI", 21, "bold"),
                 anchor="w").pack(fill="x", padx=22)
        tk.Label(kiri, text="Iterasi titik tetap  x \u2192 g(x)  untuk "
                            "persamaan kuadrat F(x) = 0",
                 bg=WARNA["navy"], fg=WARNA["teks_panel"],
                 font=("Segoe UI", 9), anchor="w", wraplength=285,
                 justify="left").pack(fill="x", padx=22, pady=(2, 10))

        tk.Label(kiri, text="PILIH CARA", bg=WARNA["navy"],
                 fg=WARNA["teks_panel"], font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x", padx=22, pady=(4, 6))

        self.tombol_cara = {}
        for n in (1, 2, 3):
            judul, _ = DESKRIPSI_CARA[n]
            b = tk.Button(kiri, text=judul, anchor="w",
                          font=("Segoe UI", 10, "bold"),
                          bg=WARNA["navy2"], fg=WARNA["putih"],
                          activebackground=WARNA["emas"],
                          activeforeground=WARNA["emas_teks"],
                          relief="flat", bd=0, padx=14, pady=9,
                          cursor="hand2",
                          command=lambda k=n: self.pilih_cara(k))
            b.pack(fill="x", padx=22, pady=3)
            self.tombol_cara[n] = b

        self.lbl_deskripsi = tk.Label(
            kiri, text="", bg=WARNA["navy"], fg=WARNA["teks_panel"],
            font=("Segoe UI", 9), anchor="w", wraplength=285,
            justify="left")
        self.lbl_deskripsi.pack(fill="x", padx=22, pady=(6, 8))

        # --- kolom masukan ---
        self.entri = {}
        for kunci, label, contoh in (
            ("persamaan", "Persamaan F(x)", "x^2 - 2x - 3"),
            ("x0", "Nilai awal (x0)", "4"),
            ("tol", "Toleransi galat", "0.0001"),
            ("maks", "Batas maksimum iterasi", "50"),
        ):
            tk.Label(kiri, text=label, bg=WARNA["navy"],
                     fg=WARNA["teks_panel"], font=("Segoe UI", 9, "bold"),
                     anchor="w").pack(fill="x", padx=22, pady=(5, 2))
            e = tk.Entry(kiri, font=("Consolas", 11),
                         bg=WARNA["putih"], fg=WARNA["teks"],
                         relief="flat", insertbackground=WARNA["teks"])
            e.pack(fill="x", padx=22, ipady=4)
            self.entri[kunci] = e

        btn = tk.Frame(kiri, bg=WARNA["navy"])
        btn.pack(fill="x", padx=22, pady=(12, 0))
        tk.Button(btn, text="HITUNG", command=self.hitung,
                  font=("Segoe UI", 11, "bold"),
                  bg=WARNA["emas"], fg=WARNA["emas_teks"],
                  activebackground="#ffc95e",
                  activeforeground=WARNA["emas_teks"],
                  relief="flat", bd=0, padx=18, pady=8,
                  cursor="hand2").pack(side="left")
        tk.Button(btn, text="Contoh", command=self.isi_contoh,
                  font=("Segoe UI", 10),
                  bg=WARNA["navy2"], fg=WARNA["putih"],
                  activebackground=WARNA["navy2"],
                  activeforeground=WARNA["emas"],
                  relief="flat", bd=0, padx=14, pady=8,
                  cursor="hand2").pack(side="left", padx=(10, 0))

        tk.Label(kiri,
                 text="Kelompok 5 \u00b7 Komputasi Numerik A \u00b7 "
                      "UI: Nabil Aulia Dika",
                 bg=WARNA["navy"], fg="#8ea3c8",
                 font=("Segoe UI", 8), anchor="w", justify="left",
                 wraplength=285).pack(fill="x", padx=22, pady=(10, 12),
                                      side="bottom")

    # ---------- panel kanan ----------
    def _bangun_panel_kanan(self):
        kanan = tk.Frame(self, bg=WARNA["latar"])
        kanan.pack(side="left", fill="both", expand=True)

        self.lbl_hasil = tk.Label(
            kanan, text="Hasil akan tampil di sini. Isi persamaan lalu "
                       "tekan HITUNG.",
            bg=WARNA["netral_bg"], fg=WARNA["netral_fg"],
            font=("Segoe UI", 12, "bold"), anchor="w",
            padx=16, pady=12)
        self.lbl_hasil.pack(fill="x", padx=18, pady=(18, 10))

        # tabel iterasi
        bingkai = tk.Frame(kanan, bg=WARNA["latar"])
        bingkai.pack(fill="both", expand=True, padx=18)
        kolom = ("iterasi", "xr", "g_xr", "f_xr", "galat")
        self.tabel = ttk.Treeview(bingkai, columns=kolom,
                                  show="headings", style="Tabel.Treeview")
        for kunci, judul, lebar in (
            ("iterasi", "Iterasi", 80),
            ("xr", "xr", 150),
            ("g_xr", "g(xr)", 150),
            ("f_xr", "F(g(xr))", 150),
            ("galat", "Galat", 150),
        ):
            self.tabel.heading(kunci, text=judul)
            self.tabel.column(kunci, width=lebar, anchor="center",
                              stretch=True)
        self.tabel.tag_configure("ganjil", background="#eef2f9")
        scroll = ttk.Scrollbar(bingkai, orient="vertical",
                               command=self.tabel.yview)
        self.tabel.configure(yscrollcommand=scroll.set)
        self.tabel.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bawah = tk.Frame(kanan, bg=WARNA["latar"])
        bawah.pack(fill="x", padx=18, pady=(12, 16))
        bawah.columnconfigure(0, weight=1)
        bawah.columnconfigure(1, weight=0)

        kiri_bawah = tk.Frame(bawah, bg=WARNA["latar"])
        kiri_bawah.grid(row=0, column=0, sticky="nsew")
        tk.Label(kiri_bawah, text="CATATAN PROSES",
                 bg=WARNA["latar"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x")
        self.txt_catatan = tk.Text(
            kiri_bawah, height=8, width=46, font=("Consolas", 9),
            bg="#111827", fg="#d7dee9", relief="flat",
            padx=10, pady=8, wrap="word", state="disabled")
        self.txt_catatan.pack(fill="both", expand=True, pady=(4, 0))

        kanan_bawah = tk.Frame(bawah, bg=WARNA["latar"], width=300)
        kanan_bawah.grid(row=0, column=1, sticky="ns", padx=(14, 0))
        kanan_bawah.pack_propagate(False)
        tk.Label(kanan_bawah, text="GRAFIK GALAT (SKALA LOG)",
                 bg=WARNA["latar"], fg=WARNA["teks_redup"],
                 font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x")
        self.kanvas = tk.Canvas(kanan_bawah, width=284, height=148,
                                bg=WARNA["putih"], highlightthickness=1,
                                highlightbackground="#d5dce8")
        self.kanvas.pack(fill="both", expand=True, pady=(4, 0))

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

    def _baca_angka(self, kunci, label, bilangan_bulat=False):
        teks = self.entri[kunci].get().strip().replace(",", ".")
        try:
            nilai = int(teks) if bilangan_bulat else float(teks)
        except ValueError:
            raise ValueError(
                f"Kolom '{label}' harus berupa angka, isi sekarang: "
                f"'{teks or '(kosong)'}'.")
        return nilai

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
        lebar = max(cv.winfo_width(), 280)
        tinggi = max(cv.winfo_height(), 130)
        if not riwayat:
            cv.create_text(lebar / 2, tinggi / 2,
                           text="Belum ada data iterasi",
                           fill=WARNA["teks_redup"],
                           font=("Segoe UI", 9))
            return
        galat = [max(r["galat"], 1e-16) for r in riwayat]
        log_g = [math.log10(v) for v in galat]
        lo, hi = min(log_g), max(log_g)
        if hi - lo < 1e-9:
            hi = lo + 1
        pad_k, pad_a, pad_b = 34, 10, 18
        titik = []
        for i, lg in enumerate(log_g):
            x = pad_k + (lebar - pad_k - 8) * (
                i / max(len(log_g) - 1, 1))
            y = pad_a + (tinggi - pad_a - pad_b) * (hi - lg) / (hi - lo)
            titik.append((x, y))
        for frac in (0, 0.5, 1):
            y = pad_a + (tinggi - pad_a - pad_b) * frac
            cv.create_line(pad_k, y, lebar - 8, y, fill="#e5eaf2")
        cv.create_text(4, pad_a + 2, anchor="nw",
                       text=f"1e{hi:.0f}", fill=WARNA["teks_redup"],
                       font=("Consolas", 7))
        cv.create_text(4, tinggi - pad_b - 8, anchor="nw",
                       text=f"1e{lo:.0f}", fill=WARNA["teks_redup"],
                       font=("Consolas", 7))
        if len(titik) > 1:
            cv.create_line(*[c for p in titik for c in p],
                           fill="#2563eb", width=2, smooth=True)
        for (x, y) in titik:
            cv.create_oval(x - 3, y - 3, x + 3, y + 3,
                           fill=WARNA["emas"], outline="#b97f10")

    def hitung(self):
        # 1. Baca & sahkan masukan. Pemeriksaan baca persamaan memakai
        # parser modul Cara 2 (paling lengkap) dan hanya untuk dialog
        # kesalahan; iterasi sendiri tetap dikerjakan modul tiap cara.
        teks_pers = self.entri["persamaan"].get().strip()
        if not teks_pers:
            messagebox.showwarning(
                "Persamaan kosong",
                "Isi dulu persamaan F(x), contoh: x^2 - 2x - 3")
            return
        try:
            x0 = self._baca_angka("x0", "Nilai awal (x0)")
            tol = self._baca_angka("tol", "Toleransi galat")
            maks = self._baca_angka("maks", "Batas maksimum iterasi",
                                    bilangan_bulat=True)
            if tol <= 0:
                raise ValueError("Toleransi harus lebih besar dari 0.")
            if maks <= 0:
                raise ValueError("Batas maksimum iterasi harus >= 1.")
            rumus = mesin2.format_persamaan(teks_pers)
            mesin2.hitung_fx(0, rumus)
            mesin2.hitung_fx(1, rumus)
        except Exception as err:
            messagebox.showerror("Masukan tidak sah", str(err))
            return

        # 2. Jalankan cara yang dipilih lewat modul anggota kelompok
        cara = self.cara_terpilih.get()
        hasil = hitung_dengan_modul(cara, teks_pers, x0, tol, maks)

        # 3. Isi tabel
        for baris_id in self.tabel.get_children():
            self.tabel.delete(baris_id)
        for idx, r in enumerate(hasil["riwayat"]):
            self.tabel.insert(
                "", "end",
                values=(r["iterasi"], fmt_angka(r["xr"]),
                        fmt_angka(r["g_xr"]), fmt_angka(r["f_xr"]),
                        fmt_angka(r["galat"])),
                tags=("ganjil",) if idx % 2 else ())

        # 4. Spanduk hasil
        status = hasil["status"]
        akar = hasil["akar"]
        if status == "konvergen":
            n_iter = hasil["riwayat"][-1]["iterasi"]
            teks = (f"\u2713  Akar \u2248 {akar:.6f}   \u00b7   konvergen "
                    f"pada iterasi ke-{n_iter}   \u00b7   Cara {cara}")
            bg, fg = WARNA["sukses_bg"], WARNA["sukses_fg"]
        elif status == "maks":
            teks = (f"Akar pendekatan \u2248 {akar:.6f} - belum konvergen "
                    f"dalam {maks} iterasi (Cara {cara})")
            bg, fg = WARNA["waspada_bg"], WARNA["waspada_fg"]
        else:  # berhenti
            teks = (f"Iterasi berhenti sebelum konvergen (Cara {cara}) - "
                    "lihat catatan proses.")
            bg, fg = WARNA["gagal_bg"], WARNA["gagal_fg"]
        self.lbl_hasil.configure(text=teks, bg=bg, fg=fg)

        # 5. Catatan & grafik
        self._tulis_catatan(hasil["catatan"])
        self._gambar_grafik(hasil["riwayat"])


if __name__ == "__main__":
    Aplikasi().mainloop()


