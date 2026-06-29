import pandas as pd
from sklearn.cluster import KMeans

# =====================================================
# CLUSTERIZAÇÃO GEOGRÁFICA
# =====================================================

K = 5

LIMITES_SP = {
    "lat_min": -24.35,
    "lat_max": -22.85,
    "lon_min": -47.45,
    "lon_max": -45.55,
}

df = pd.read_excel(
    "base_clusterizacao.xlsx"
)

df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

df["fora_recorte_mapa"] = ~(
    df["latitude"].between(LIMITES_SP["lat_min"], LIMITES_SP["lat_max"])
    & df["longitude"].between(LIMITES_SP["lon_min"], LIMITES_SP["lon_max"])
)

df_cluster = df[~df["fora_recorte_mapa"]].copy()

if len(df_cluster) < K:
    raise ValueError("Registros insuficientes para clusterizar dentro do recorte.")

# Dados para clusterização. O recorte evita que geocodificações distantes
# dominem os centroides e apaguem os agrupamentos da região principal.
X = df_cluster[["latitude", "longitude"]]

# Modelo K-Means
kmeans = KMeans(
    n_clusters=K,
    random_state=42,
    n_init=10
)

# Criar clusters
df["cluster"] = pd.NA
df.loc[df_cluster.index, "cluster"] = kmeans.fit_predict(X)

# Salvar resultado
df.to_excel(
    "base_clusterizada.xlsx",
    index=False
)

df[df["fora_recorte_mapa"]].to_excel(
    "coordenadas_fora_recorte.xlsx",
    index=False
)

print("Arquivo criado: base_clusterizada.xlsx")
print("Arquivo criado: coordenadas_fora_recorte.xlsx")
print("\nRegistros no recorte:", len(df_cluster))
print("Registros fora do recorte:", int(df["fora_recorte_mapa"].sum()))

print("\nDistribuição dos clusters:")

print(
    df_cluster.assign(cluster=df.loc[df_cluster.index, "cluster"])["cluster"]
    .value_counts()
    .sort_index()
)

print("\nCentroides:")

centroides = pd.DataFrame(
    kmeans.cluster_centers_,
    columns=["latitude", "longitude"]
)

print(centroides)
