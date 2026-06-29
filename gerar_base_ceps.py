# =====================================================
# OBJETIVO
# =====================================================
#
# Em vez de trabalhar com 2609 registros completos,
# vamos trabalhar apenas com os 2140 CEPs únicos.
#
# Será criada uma base intermediária:
# ceps_unicos.xlsx
#
# Em seguida será criada uma segunda base:
# cep_coordenadas.xlsx
#
# Estrutura:
# CEP | latitude | longitude
#
# Por fim, faremos um merge entre a tabela de
# coordenadas e as três planilhas originais,
# preenchendo automaticamente latitude e longitude.
#
# ======================================================





import pandas as pd
from cep_utils import normalizar_cep

arquivo = "planilha_1.xlsx"

df = pd.read_excel(
    arquivo,
    sheet_name="Respostas ao formulário 1"
)

df["CEP"] = df["CEP"].apply(normalizar_cep)

ceps = (
    df["CEP"]
    .dropna()
    .drop_duplicates()
    .sort_values()
)

ceps_df = pd.DataFrame({
    "CEP": ceps
})

ceps_df.to_excel(
    "ceps_unicos.xlsx",
    index=False
)

print(
    f"CEPs únicos salvos: {len(ceps_df)}"
)
