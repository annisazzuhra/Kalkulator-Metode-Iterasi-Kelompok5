import math
import re

def format_persamaan(teks):
    #Disini mengubah ketikan biasa (misal: x^2 - 2x - 3) menjadi ke format Python (x**2 - 2*x - 3)
    teks = teks.replace(" ", "").replace("^", "**")
    teks = re.sub(r'(\d)([xX])', r'\1*\2', teks)
    return teks.lower()

def hitung_fx(x, rumus_python):
    """Menghitung nilai F(x) dari persamaan yang diinput pengguna"""
    return eval(rumus_python, {"__builtins__": None}, {"x": x, "sqrt": math.sqrt})

def kalkulator_cara1(input_fx, x0, toleransi=0.0001, max_iter=50):
    """
    Fungsi utama Kalkulator Metode Iterasi Cara 1:
    Memindahkan suku selain x^2 ke ruas kanan, lalu mengakarkan kedua ruas.
    """
    rumus_fx = format_persamaan(input_fx)

    #Mencari koefisien x^2 (nilai a) secara otomatis agar rumus akar Cara Iterasi 1 akurat
    c = hitung_fx(0, rumus_fx)
    a = ((hitung_fx(1, rumus_fx) + hitung_fx(-1, rumus_fx)) / 2) - c
    if a == 0:
        a = 1

    print("\n" + "=" * 70)
    print(f"{'Iterasi':<10} | {'xr':<12} | {'g(xr)':<12} | {'F(xr)':<12} | {'Galat':<12}")
    print("=" * 70)

    xr = x0
    riwayat_data = []

    for i in range(1, max_iter + 1):
        #Rumus Cara Iterasi 1: x^2 = (a*x^2 - F(x)) / a  menjadi  g(x) = sqrt((a*x^2 - F(x)) / a)
        dalam_akar = (a * (xr ** 2) - hitung_fx(xr, rumus_fx)) / a

        if dalam_akar < 0:
            print("=" * 70)
            print(f"Berhenti pada iterasi ke-{i}: Nilai di dalam akar negatif ({dalam_akar:.6f}).")
            return None, riwayat_data

        xr_baru = math.sqrt(dalam_akar)
        fx_baru = hitung_fx(xr_baru, rumus_fx)
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

    print("=" * 70)
    print("Iterasi mencapai batas maksimum (belum konvergen).")
    return xr, riwayat_data

if __name__ == "__main__":
    print("=== KALKULATOR METODE ITERASI CARA 1 ===")
    
    persamaan = input("1. Masukkan persamaan F(x)        : ")
    x0        = float(input("2. Masukkan nilai awal (x0)       : "))
    toleransi = float(input("3. Masukkan toleransi error       : "))
    max_iter  = int(input("4. Masukkan batas maks iterasi    : "))

    kalkulator_cara1(persamaan, x0, toleransi, max_iter)