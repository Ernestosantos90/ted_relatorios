import pandas as pd

df = pd.read_excel(
    "cep_coordenadas.xlsx",
    dtype={"CEP": str}
)

print("Total de coordenadas:", len(df))

print("\nLatitude vazia:")
print(df["latitude"].isna().sum())

print("\nLongitude vazia:")
print(df["longitude"].isna().sum())

print("\nPrimeiras linhas:")
print(df.head())