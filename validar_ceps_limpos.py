import pandas as pd

df = pd.read_excel(
    "ceps_unicos_limpo.xlsx",
    dtype={"CEP": str}
)

print(df.head(20))

print("\nTamanhos:")
print(
    df["CEP"]
    .str.len()
    .value_counts()
)