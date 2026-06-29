print(
    alunos["CEP"]
    .astype(str)
    .str.len()
    .value_counts()
)