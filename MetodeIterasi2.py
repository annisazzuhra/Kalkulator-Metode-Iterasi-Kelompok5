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
