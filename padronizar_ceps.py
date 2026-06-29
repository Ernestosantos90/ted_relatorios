import pandas as pd
import re

arquivo = "planilha_1.xlsx"

df = pd.read_excel(
    arquivo,
    sheet_name="Respostas ao formulário 1"
)

def padronizar_cep(cep):

    if pd.isna(cep):
        return None

    cep = str(cep)

    # Remove tudo que não for número
    cep = re.sub(r"\D", "", cep)

    # Completa com zeros à esquerda
    cep = cep.zfill(8)

    return cep

df["CEP"] = df["CEP"].apply(
    padronizar_cep
)

print(df["CEP"].head(20))

print("\nCEPs vazios:")
print(df["CEP"].isna().sum())

print("\nCEPs únicos:", df["CEP"].nunique())
print("Total registros:", len(df))