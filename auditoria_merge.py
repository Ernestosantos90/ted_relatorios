import pandas as pd

# Base alunos
alunos = pd.read_excel(
    "planilha_1.xlsx",
    dtype={"CEP": str}
)

# Base coordenadas
coords = pd.read_excel(
    "cep_coordenadas.xlsx",
    dtype={"CEP": str}
)

print("===== BASE ALUNOS =====")
print("Linhas:", len(alunos))
print("CEPs distintos:", alunos["CEP"].nunique())

print("\n===== BASE COORDENADAS =====")
print("Linhas:", len(coords))
print("CEPs distintos:", coords["CEP"].nunique())

# CEPs repetidos na base de coordenadas
duplicados = coords[
    coords.duplicated(
        subset=["CEP"],
        keep=False
    )
]

print("\n===== CEPs DUPLICADOS EM COORDENADAS =====")
print("Quantidade:", len(duplicados))

if len(duplicados) > 0:
    print(
        duplicados
        .sort_values("CEP")
        .head(20)
    )
    print(
    alunos["CEP"]
    .astype(str)
    .str.len()
    .value_counts()
)