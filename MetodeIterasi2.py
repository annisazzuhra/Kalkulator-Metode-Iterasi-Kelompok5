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
