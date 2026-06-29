import pandas as pd

arquivo = "planilha_1.xlsx"

df = pd.read_excel(
    arquivo,
    sheet_name="Respostas ao formulário 1"
)

print("Registros:", len(df))

print(
    "CEPs únicos:",
    df["CEP"].dropna().nunique()
)

print(
    "CEPs repetidos:",
    len(df) - df["CEP"].dropna().nunique()
)