import math
import re

FUNGSI_AMAN = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "exp": math.exp, "log": math.log, "abs": abs,
}

def format_persamaan(teks):
    teks = teks.lower().replace(" ", "").replace("^", "**").replace(",", ".")
    if teks.endswith("=0"):
        teks = teks[:-2]
    teks = re.sub(r'(\d)([x(])', r'\1*\2', teks)
    teks = re.sub(r'(x)\(', r'\1*(', teks)
    teks = re.sub(r'\)([x(\d])', r')*\1', teks)
    return teks

def hitung_fx(x, rumus_python):
    return eval(rumus_python, {"__builtins__": None}, {"x": x, **FUNGSI_AMAN})

def baca_angka(pesan, tipe=float, harus_positif=False):
    while True:
        teks = input(pesan).strip().replace(",", ".")
        try:
            nilai = tipe(teks)
        except ValueError:
            jenis = "bilangan bulat" if tipe is int else "angka"
            print(f"   ! Isi harus berupa {jenis}, coba lagi.")
            continue
        if harus_positif and nilai <= 0:
            print("   ! Angka harus lebih besar dari 0, coba lagi.")
            continue
        return nilai

def baca_persamaan(pesan):
    while True:
        teks = input(pesan)
        rumus = format_persamaan(teks)
        try:
            hitung_fx(0, rumus)
            hitung_fx(1, rumus)
            return teks
        except Exception:
            print("   ! Persamaan tidak bisa dibaca. Contoh yang benar: x^2 - 2x - 3")

def kalkulator_cara3(input_fx, x0, toleransi=0.0001, max_iter=50):
    """
    Iterasi Cara 3: Memfaktorkan persamaan menjadi x(x-2) = 3, 
    sehingga fungsi iterasi g(x) = 3 / (x - 2)
    """
    rumus_fx = format_persamaan(input_fx)

    print(f"\nRumus iterasi Cara 3: g(x) = 3 / (x - 2)")
    print("=" * 70)
    print(f"{'Iterasi':<10} | {'xr':<12} | {'g(xr)':<12} | {'F(xr)':<12} | {'Galat':<12}")
    print("=" * 70)

    xr = x0
    riwayat_data = []

    for i in range(1, max_iter + 1):
        if xr - 2 == 0:
            print("=" * 70)
            print(f"Berhenti di iterasi ke-{i}: Penyebut bernilai nol (x = 2, pembagian dengan nol).")
            print("Saran: ganti nilai awal (x0) agar tidak sama dengan 2.")
            return None, riwayat_data

        try:
            xr_baru = 3 / (xr - 2)
            fx_baru = hitung_fx(xr_baru, rumus_fx)
            if isinstance(xr_baru, complex) or abs(xr_baru) > 1e12:
                raise OverflowError
        except (ArithmeticError, ValueError, TypeError):
            print("=" * 70)
            print(f"Berhenti di iterasi ke-{i}: angka terlalu besar atau tidak terdefinisi (divergen).")
            print("Saran: coba nilai awal (x0) yang lain.")
            return None, riwayat_data

        galat = abs(xr_baru - xr)
        print(f"{i:<10} | {xr:<12.6f} | {xr_baru:<12.6f} | {fx_baru:<12.6f} | {galat:<12.6f}")

        riwayat_data.append({
            "iterasi": i, "xr": xr, "g_xr": xr_baru, "f_xr": fx_baru, "galat": galat
        })

        if galat < toleransi:
            print("=" * 70)
            print(f"Hasil Akhir (Akar x) : {xr_baru:.6f}")
            print(f"Ditemukan pada       : Iterasi ke-{i}")
            print("=" * 70)
            return xr_baru, riwayat_data

        xr = xr_baru



