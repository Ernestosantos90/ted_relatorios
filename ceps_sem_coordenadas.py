import pandas as pd

base = pd.read_excel(
    "planilha_1_geocodificada.xlsx",
    dtype={"CEP": str}
)

faltantes = base[
    base["latitude"].isna()
]

print("Alunos sem coordenadas:", len(faltantes))

print(
    "CEPs distintos sem coordenadas:",
    faltantes["CEP"].nunique()
)

faltantes[["CEP"]].drop_duplicates().to_excel(
    "ceps_sem_coordenadas.xlsx",
    index=False
)

print(
    "Arquivo criado: ceps_sem_coordenadas.xlsx"
)