import pandas as pd

alunos = pd.read_excel(
    "planilha_1.xlsx",
    dtype={"CEP": str}
)

print("Total registros:", len(alunos))

print("\nExemplos de CEP:")
print(alunos["CEP"].head(30))

print("\nTamanho dos CEPs:")
print(
    alunos["CEP"]
    .astype(str)
    .str.len()
    .value_counts()
)