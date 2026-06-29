import pandas as pd
from cep_utils import normalizar_cep

df = pd.read_excel("ceps_unicos.xlsx")

df["CEP"] = df["CEP"].apply(normalizar_cep)
df = df.dropna(subset=["CEP"])
df = df.drop_duplicates(subset=["CEP"]).sort_values("CEP")

print(df.head(20))

df.to_excel(
    "ceps_unicos_limpo.xlsx",
    index=False
)

print(f"\nTotal CEPs: {len(df)}")
print("Arquivo salvo: ceps_unicos_limpo.xlsx")
