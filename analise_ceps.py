import pandas as pd

arquivo = "planilha_1.xlsx"

df = pd.read_excel(
    arquivo,
    sheet_name="Respostas ao formulário 1"
)

print("Total de registros:", len(df))

print("\nCEPs vazios:")
print(df["CEP"].isna().sum())

print("\nPrimeiros CEPs:")
print(df["CEP"].head(20))