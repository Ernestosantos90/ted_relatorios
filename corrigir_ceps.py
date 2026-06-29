import pandas as pd

arquivo = "planilha_1.xlsx"

df = pd.read_excel(
    arquivo,
    sheet_name="Respostas ao formulário 1"
)

df["CEP"] = (
    df["CEP"]
    .astype(str)
    .str.upper()
    .str.replace("O", "0")
)

print(
    df["CEP"]
    .str[:2]
    .value_counts()
    .head(20)
)