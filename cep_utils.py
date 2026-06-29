import re

import pandas as pd


def normalizar_cep(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip().upper().replace("O", "0")

    if re.fullmatch(r"\d+\.0+", texto):
        texto = texto.split(".", 1)[0]

    digitos = re.sub(r"\D", "", texto)

    if not digitos:
        return None

    if len(digitos) > 8:
        digitos = digitos[-8:]

    return digitos.zfill(8)
