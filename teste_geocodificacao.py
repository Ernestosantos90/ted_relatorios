import pandas as pd
import requests
from geopy.geocoders import Nominatim

# =====================================================
# TESTE DE GEOCODIFICAÇÃO DE UM CEP
# =====================================================
#
# Fluxo:
# CEP
# ↓
# ViaCEP
# ↓
# Logradouro + Bairro + Cidade + UF
# ↓
# OpenStreetMap (Nominatim)
# ↓
# Latitude e Longitude
#
# =====================================================

# Ler arquivo de CEPs
df = pd.read_excel(
    "ceps_unicos_limpo.xlsx",
    dtype={"CEP": str}
)

# Primeiro CEP da lista
cep = df["CEP"].iloc[0]

print(f"Consultando CEP: {cep}")

# Consulta ViaCEP
url = f"https://viacep.com.br/ws/{cep}/json/"

resposta = requests.get(url)

dados = resposta.json()

print("\nStatus:", resposta.status_code)

print("\nDados:")
print(dados)

# Montar endereço completo
endereco = (
    f"{dados['logradouro']}, "
    f"{dados['localidade']}, "
    f"{dados['uf']}, Brasil"
)

print("\nEndereço montado:")
print(endereco)

# Geocodificação
geolocator = Nominatim(
    user_agent="projeto_geocodificacao"
)

local = geolocator.geocode(endereco)

print("\nResultado geocodificação:")
print(local)

# Coordenadas
if local:
    print("\nLatitude:", local.latitude)
    print("Longitude:", local.longitude)
else:
    print("\nEndereço não encontrado.")