import pandas as pd

df = pd.read_excel(
    "planilha_1_geocodificada.xlsx"
)

print(df.columns.tolist())

print("\nRegistros com coordenadas:")
print(
    df[
        df["latitude"].notna()
    ].shape[0]
)