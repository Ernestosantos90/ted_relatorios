import pandas as pd

df = pd.read_excel("planilha_1.xlsx")

print(df.columns.tolist())
print("\nTotal de registros:", len(df))