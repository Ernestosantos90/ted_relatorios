import pandas as pd
from cep_utils import normalizar_cep

df = pd.read_excel(
    "cep_coordenadas.xlsx",
    dtype={"CEP": str}
)

df["CEP"] = df["CEP"].apply(normalizar_cep)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df = df.dropna(subset=["CEP", "latitude", "longitude"])

print("Antes:")
print("Linhas:", len(df))
print("CEPs distintos:", df["CEP"].nunique())

# Remove registros exatamente iguais
df = df.drop_duplicates()

# Mantém apenas um registro por CEP
df = df.drop_duplicates(
    subset=["CEP"],
    keep="first"
)

print("\nDepois:")
print("Linhas:", len(df))
print("CEPs distintos:", df["CEP"].nunique())

df.to_excel(
    "cep_coordenadas_limpo.xlsx",
    index=False
)

print("\nArquivo salvo: cep_coordenadas_limpo.xlsx")
