import pandas as pd

df = pd.read_excel(
    "planilha_1_geocodificada.xlsx"
)

df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# Mantém apenas registros com coordenadas
df_cluster = df[
    df["latitude"].notna() &
    df["longitude"].notna() &
    df["latitude"].between(-90, 90) &
    df["longitude"].between(-180, 180)
].copy()

print("Registros para clusterização:", len(df_cluster))

# Salvar base limpa
df_cluster.to_excel(
    "base_clusterizacao.xlsx",
    index=False
)

print("Arquivo criado: base_clusterizacao.xlsx")
