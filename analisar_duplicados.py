import pandas as pd

df = pd.read_excel(
    "cep_coordenadas.xlsx",
    dtype={"CEP": str}
)

duplicados = df[
    df.duplicated(
        subset=["CEP"],
        keep=False
    )
]

resumo = (
    duplicados
    .groupby("CEP")
    .agg({
        "latitude": "nunique",
        "longitude": "nunique"
    })
)

print(
    resumo[
        (resumo["latitude"] > 1)
        | (resumo["longitude"] > 1)
    ]
)