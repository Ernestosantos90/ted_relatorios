import pandas as pd
import requests
import time
import os
from geopy.geocoders import Nominatim

# =====================================================
# GERAR COORDENADAS DOS CEPs
# =====================================================

ARQUIVO_CEPS = "ceps_unicos_limpo.xlsx"
ARQUIVO_SAIDA = "cep_coordenadas.xlsx"

# Ler CEPs
df = pd.read_excel(
    ARQUIVO_CEPS,
    dtype={"CEP": str}
)

# Inicializar geolocalizador
geolocator = Nominatim(
    user_agent="projeto_geocodificacao"
)

resultado = []

total = len(df)

for i, cep in enumerate(df["CEP"], start=1):

    print(f"[{i}/{total}] CEP: {cep}")

    try:

        # Consulta ViaCEP
        url = f"https://viacep.com.br/ws/{cep}/json/"
        resposta = requests.get(url, timeout=10)

        dados = resposta.json()

        if "erro" in dados:
            print("CEP inválido")
            continue

        endereco = (
            f"{dados['logradouro']}, "
            f"{dados['localidade']}, "
            f"{dados['uf']}, Brasil"
        )

        # Consulta coordenadas
        local = geolocator.geocode(
            endereco,
            timeout=10
        )

        if local:

            resultado.append({
                "CEP": cep,
                "latitude": local.latitude,
                "longitude": local.longitude
            })

            print(
                f"OK -> {local.latitude}, {local.longitude}"
            )

        else:

            print("Endereço não localizado")

        # Salva a cada CEP processado
        pd.DataFrame(resultado).to_excel(
            ARQUIVO_SAIDA,
            index=False
        )

        time.sleep(1)

    except Exception as e:

        print("Erro:", e)

print("\nProcessamento concluído!")
print(f"Coordenadas geradas: {len(resultado)}")
print(f"Arquivo salvo: {ARQUIVO_SAIDA}")