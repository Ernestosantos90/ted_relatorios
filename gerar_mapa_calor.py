import argparse
import json
from pathlib import Path

import pandas as pd


ARQUIVO_ENTRADA = "base_clusterizada.xlsx"
ARQUIVO_SAIDA = "mapa_calor.html"

# Recorte amplo para Grande Sao Paulo e arredores. Evita que coordenadas
# geocodificadas muito distantes comprimam o mapa principal.
LIMITES_SP = {
    "lat_min": -24.35,
    "lat_max": -22.85,
    "lon_min": -47.45,
    "lon_max": -45.55,
}


def carregar_dados(caminho, filtrar_sp=True):
    df = pd.read_excel(caminho)

    for coluna in ["latitude", "longitude"]:
        if coluna not in df.columns:
            raise ValueError(f"Coluna obrigatoria ausente: {coluna}")
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    df = df.dropna(subset=["latitude", "longitude"]).copy()
    df = df[
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
    ].copy()

    total_validos = len(df)

    if filtrar_sp:
        df = df[
            df["latitude"].between(LIMITES_SP["lat_min"], LIMITES_SP["lat_max"])
            & df["longitude"].between(LIMITES_SP["lon_min"], LIMITES_SP["lon_max"])
        ].copy()

    if df.empty:
        raise ValueError("Nao ha coordenadas validas para gerar o mapa.")

    return df, total_validos


def montar_payload(df):
    agrupado = (
        df.groupby(["latitude", "longitude"], dropna=True)
        .size()
        .reset_index(name="peso")
    )

    pontos_calor = agrupado[["latitude", "longitude", "peso"]].round(6).values.tolist()

    pontos = []
    colunas = set(df.columns)
    for _, linha in df.iterrows():
        item = {
            "lat": round(float(linha["latitude"]), 6),
            "lon": round(float(linha["longitude"]), 6),
        }
        if "cluster" in colunas and pd.notna(linha["cluster"]):
            item["cluster"] = int(linha["cluster"])
        if "CEP" in colunas and pd.notna(linha["CEP"]):
            item["cep"] = str(linha["CEP"]).zfill(8)
        if "Nome Completo" in colunas and pd.notna(linha["Nome Completo"]):
            item["nome"] = str(linha["Nome Completo"])
        pontos.append(item)

    centro = {
        "lat": round(float(df["latitude"].mean()), 6),
        "lon": round(float(df["longitude"].mean()), 6),
    }

    return pontos_calor, pontos, centro


def gerar_html(pontos_calor, pontos, centro, resumo):
    heat_json = json.dumps(pontos_calor, ensure_ascii=False)
    pontos_json = json.dumps(pontos, ensure_ascii=False)
    centro_json = json.dumps(centro, ensure_ascii=False)
    resumo_json = json.dumps(resumo, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mapa de Calor</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map {{
      height: 100%;
      margin: 0;
      font-family: Arial, sans-serif;
    }}
    .painel {{
      position: absolute;
      z-index: 1000;
      top: 12px;
      left: 12px;
      max-width: 320px;
      padding: 12px 14px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.94);
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.18);
      color: #1f2937;
      font-size: 13px;
      line-height: 1.35;
    }}
    .painel h1 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .painel button {{
      display: block;
      width: 100%;
      margin-top: 10px;
      padding: 7px 9px;
      border: 1px solid #9ca3af;
      border-radius: 6px;
      background: #fff;
      cursor: pointer;
    }}
    .painel a.botao {{
      display: block;
      width: 100%;
      box-sizing: border-box;
      margin-top: 8px;
      padding: 7px 9px;
      border: 1px solid #9ca3af;
      border-radius: 6px;
      background: #fff;
      color: #1f2937;
      text-align: center;
      text-decoration: none;
      font-size: 13px;
    }}
    .painel a.botao:hover,
    .painel button:hover {{
      background: #f3f4f6;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  <section class="painel">
    <h1>Mapa de Calor</h1>
    <div id="resumo"></div>
    <button id="alternar">Mostrar/ocultar pontos</button>
    <a class="botao" href="relatorio_ministerio_empreendedorismo.html">Abrir relatório</a>
  </section>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
  <script>
    const heatData = {heat_json};
    const pontos = {pontos_json};
    const centro = {centro_json};
    const resumo = {resumo_json};

    const map = L.map("map").setView([centro.lat, centro.lon], 10);
    L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap"
    }}).addTo(map);

    L.heatLayer(heatData, {{
      radius: 28,
      blur: 22,
      maxZoom: 15,
      minOpacity: 0.34,
      gradient: {{
        0.20: "#2563eb",
        0.45: "#22c55e",
        0.70: "#facc15",
        1.00: "#dc2626"
      }}
    }}).addTo(map);

    const bounds = L.latLngBounds(heatData.map((p) => [p[0], p[1]]));
    map.fitBounds(bounds.pad(0.12));

    const cores = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2"];
    const camadaPontos = L.layerGroup();
    pontos.forEach((p) => {{
      const cluster = Number.isInteger(p.cluster) ? p.cluster : 0;
      const marcador = L.circleMarker([p.lat, p.lon], {{
        radius: 4,
        color: cores[Math.abs(cluster) % cores.length],
        weight: 1,
        fillOpacity: 0.68
      }});
      const linhas = [
        p.nome ? `<strong>${{p.nome}}</strong>` : null,
        p.cep ? `CEP: ${{p.cep}}` : null,
        Number.isInteger(p.cluster) ? `Cluster: ${{p.cluster}}` : null
      ].filter(Boolean);
      marcador.bindPopup(linhas.join("<br>"));
      marcador.addTo(camadaPontos);
    }});

    document.getElementById("resumo").innerHTML = `
      Registros no mapa: <strong>${{resumo.registros_mapa}}</strong><br>
      Coordenadas validas: <strong>${{resumo.coordenadas_validas}}</strong><br>
      Fora do recorte: <strong>${{resumo.fora_recorte}}</strong>
    `;

    document.getElementById("alternar").addEventListener("click", () => {{
      if (map.hasLayer(camadaPontos)) {{
        map.removeLayer(camadaPontos);
      }} else {{
        camadaPontos.addTo(map);
      }}
    }});
  </script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Gera um mapa de calor HTML a partir das coordenadas.")
    parser.add_argument("--entrada", default=ARQUIVO_ENTRADA)
    parser.add_argument("--saida", default=ARQUIVO_SAIDA)
    parser.add_argument("--sem-filtro-sp", action="store_true")
    args = parser.parse_args()

    df, total_validos = carregar_dados(args.entrada, filtrar_sp=not args.sem_filtro_sp)
    pontos_calor, pontos, centro = montar_payload(df)
    resumo = {
        "registros_mapa": len(df),
        "coordenadas_validas": total_validos,
        "fora_recorte": total_validos - len(df),
    }

    html = gerar_html(pontos_calor, pontos, centro, resumo)
    Path(args.saida).write_text(html, encoding="utf-8")

    print(f"Arquivo criado: {args.saida}")
    print(f"Registros no mapa: {resumo['registros_mapa']}")
    print(f"Coordenadas validas: {resumo['coordenadas_validas']}")
    print(f"Fora do recorte: {resumo['fora_recorte']}")


if __name__ == "__main__":
    main()
