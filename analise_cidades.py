## neste arquivo estaremos analisando os dados de CEPs, para isso vamos utilizar a biblioteca pandas
##e vamos analisar os ceps por cidade, estado e região, para isso vamos utilizar a função value_counts() do pandas

import pandas as pd

arquivo = "planilha_1.xlsx"

df = pd.read_excel(
    arquivo,
    sheet_name="Respostas ao formulário 1"
)

print(
    df["CEP"]
    .astype(str)
    .str[:2]
    .value_counts()
    .head(20)
)