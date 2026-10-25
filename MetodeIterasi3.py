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


