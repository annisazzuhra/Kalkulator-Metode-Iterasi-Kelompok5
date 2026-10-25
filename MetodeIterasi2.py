import math
import re

FUNGSI_AMAN = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "exp": math.exp, "log": math.log, "abs": abs,
}
def format_persamaan(teks):
    # Ubah tulisan biasa jadi format Python, contoh: x^2 - 2x - 3 -> x**2-2*x-3
    teks = teks.lower().replace(" ", "").replace("^", "**").replace(",", ".")
    if teks.endswith("=0"):
        teks = teks[:-2]
    teks = re.sub(r'(\d)([x(])', r'\1*\2', teks)
    teks = re.sub(r'(x)\(', r'\1*(', teks)
    teks = re.sub(r'\)([x(\d])', r')*\1', teks)
    return teks


def hitung_fx(x, rumus_python):
    return eval(rumus_python, {"__builtins__": None}, {"x": x, **FUNGSI_AMAN})


def adalah_kuadrat(rumus_python):
    for t in (0, 1, 2.5):
        hasil = (hitung_fx(t + 3, rumus_python) - 3 * hitung_fx(t + 2, rumus_python)
                 + 3 * hitung_fx(t + 1, rumus_python) - hitung_fx(t, rumus_python))
        if abs(hasil) > 1e-6:
            return False
    return True


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


def kalkulator_cara2(input_fx, x0, toleransi=0.0001, max_iter=50):
    """
    Iterasi Cara 2: pindahkan suku x ke ruas kiri, lalu bagi dengan angka di depan x.
    Contoh: x^2 - 2x - 3 = 0  ->  x = (x^2 - 3) / 2
    """
    rumus_fx = format_persamaan(input_fx)

    if not adalah_kuadrat(rumus_fx):
        print("\nPERINGATAN: Persamaan ini bukan kuadrat. Program tetap jalan,")
        print("            tapi hasilnya mungkin tidak sesuai Cara 2.")


    # b = angka di depan x (untuk x^2 - 2x - 3, b = -2)
    h = 0.00001
    b = round((hitung_fx(h, rumus_fx) - hitung_fx(-h, rumus_fx)) / (2 * h), 6)
    if b == 0:
        print("\nPersamaan tidak punya suku x (pangkat 1), jadi Cara 2 tidak bisa dipakai.")
        return None, []

    print(f"\nRumus iterasi: g(x) = x - F(x)/({b:g})")
    print("=" * 70)
    print(f"{'Iterasi':<10} | {'xr':<12} | {'g(xr)':<12} | {'F(xr)':<12} | {'Galat':<12}")
    print("=" * 70)

    xr = x0
    riwayat_data = []


    for i in range(1, max_iter + 1):
        try:
            xr_baru = xr - hitung_fx(xr, rumus_fx) / b
            fx_baru = hitung_fx(xr_baru, rumus_fx)
            if isinstance(xr_baru, complex) or abs(xr_baru) > 1e12:
                raise OverflowError
        except (ArithmeticError, ValueError, TypeError):
            print("=" * 70)
            print(f"Berhenti di iterasi ke-{i}: angka terlalu besar atau tidak bisa dihitung (divergen).")
            print("Saran: coba nilai awal (x0) yang lebih dekat ke akar.")
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


    print("=" * 70)
    print("Sudah mencapai batas maksimum iterasi (belum konvergen).")

    if len(riwayat_data) >= 3 and riwayat_data[-2]["galat"] > 0:
        rasio = riwayat_data[-1]["galat"] / riwayat_data[-2]["galat"]
        if rasio >= 1:
            print("Penjelasan: galat tidak mengecil, jadi iterasi ini tidak akan konvergen.")
        elif rasio > 0.9:
            print("Penjelasan: galat mengecil, tapi sangat pelan.")
        else:
            print("Penjelasan: galat sudah mengecil, coba naikkan batas maksimum iterasi.")
        print("Saran      : ganti nilai awal, naikkan maks iterasi, atau perbesar toleransi.")
    return xr, riwayat_data


if __name__ == "__main__":
    print("=== KALKULATOR METODE ITERASI CARA 2 ===")

    persamaan = baca_persamaan("1. Masukkan persamaan F(x)        : ")
    x0        = baca_angka("2. Masukkan nilai awal (x0)       : ")
    toleransi = baca_angka("3. Masukkan toleransi error       : ", harus_positif=True)
    max_iter  = baca_angka("4. Masukkan batas maks iterasi    : ", tipe=int, harus_positif=True)

    kalkulator_cara2(persamaan, x0, toleransi, max_iter)
