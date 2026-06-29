import pandas as pd
from cep_utils import normalizar_cep

# =====================================================
# MERGE DAS COORDENADAS
# =====================================================

# Base principal
alunos = pd.read_excel(
    "planilha_1.xlsx",
    dtype={"CEP": str}
)

# Base de coordenadas
coords = pd.read_excel(
    "cep_coordenadas_limpo.xlsx",
    dtype={"CEP": str}
)

alunos["CEP"] = alunos["CEP"].apply(normalizar_cep)
coords["CEP"] = coords["CEP"].apply(normalizar_cep)

coords = coords.dropna(subset=["CEP", "latitude", "longitude"])
coords = coords.drop_duplicates(subset=["CEP"], keep="first")

# Remover colunas antigas de latitude/longitude
if "latitude" in alunos.columns:
    alunos = alunos.drop(columns=["latitude"])

if "longitude" in alunos.columns:
    alunos = alunos.drop(columns=["longitude"])

# Merge
base_final = alunos.merge(
    coords,
    on="CEP",
    how="left"
)

# Salvar
base_final.to_excel(
    "planilha_1_geocodificada.xlsx",
    index=False
)

print("Arquivo criado com sucesso!")

print("\nTotal registros:", len(base_final))

print(
    "\nLatitude preenchida:",
    base_final["latitude"].notna().sum()
)

print(
    "Longitude preenchida:",
    base_final["longitude"].notna().sum()
)

print(
    "\nLatitude vazia:",
    base_final["latitude"].isna().sum()
)

print(
    "Longitude vazia:",
    base_final["longitude"].isna().sum()
)
