from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd

from cep_utils import normalizar_cep


ARQUIVO_BASE_ORIGINAL = "planilha_1.xlsx"
ARQUIVO_BASE_GEOCODIFICADA = "planilha_1_geocodificada.xlsx"
ARQUIVO_BASE_TRATADA = "base_clusterizada.xlsx"
ARQUIVO_FORA_RECORTE = "coordenadas_fora_recorte.xlsx"
ARQUIVO_MAPA = "mapa_calor.html"
ARQUIVO_EXCEL_ENTREGA = "base_tratada_para_ministerio.xlsx"
ARQUIVO_RELATORIO = "relatorio_ministerio_empreendedorismo.html"


def pct(valor, total):
    if total == 0:
        return "0,0%"
    return f"{valor / total * 100:.1f}%".replace(".", ",")


def fmt_int(valor):
    return f"{int(valor):,}".replace(",", ".")


def tabela_html(df, colunas=None):
    if colunas:
        df = df[colunas]

    cabecalho = "".join(f"<th>{escape(str(col))}</th>" for col in df.columns)
    linhas = []
    for _, row in df.iterrows():
        tds = "".join(f"<td>{escape(str(valor))}</td>" for valor in row)
        linhas.append(f"<tr>{tds}</tr>")

    return f"<table><thead><tr>{cabecalho}</tr></thead><tbody>{''.join(linhas)}</tbody></table>"


def barras_html(df, label_col, value_col, total=None):
    if total is None:
        total = max(float(df[value_col].max()), 1.0)

    partes = []
    for _, row in df.iterrows():
        valor = float(row[value_col])
        largura = max(valor / total * 100, 1)
        partes.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{escape(str(row[label_col]))}</div>
              <div class="bar-track"><span style="width:{largura:.2f}%"></span></div>
              <div class="bar-value">{fmt_int(valor)}</div>
            </div>
            """
        )
    return "".join(partes)


def main():
    base_original = pd.read_excel(ARQUIVO_BASE_ORIGINAL, dtype={"CEP": str})
    base_geo = pd.read_excel(ARQUIVO_BASE_GEOCODIFICADA, dtype={"CEP": str})
    base = pd.read_excel(ARQUIVO_BASE_TRATADA, dtype={"CEP": str})
    fora_recorte = pd.read_excel(ARQUIVO_FORA_RECORTE, dtype={"CEP": str})

    for df in [base_original, base_geo, base, fora_recorte]:
        if "CEP" in df.columns:
            df["CEP"] = df["CEP"].apply(normalizar_cep)

    total_original = len(base_original)
    total_geocodificado = int(base_geo["latitude"].notna().sum())
    total_tratado = len(base)
    total_mapa = int((~base["fora_recorte_mapa"]).sum())
    total_fora = int(base["fora_recorte_mapa"].sum())

    cluster_counts = (
        base.dropna(subset=["cluster"])
        .assign(cluster=lambda d: d["cluster"].astype(int))
        .groupby("cluster")
        .size()
        .reset_index(name="registros")
        .sort_values("registros", ascending=False)
    )
    cluster_counts["participacao"] = cluster_counts["registros"].apply(lambda x: pct(x, total_mapa))
    cluster_counts = cluster_counts.sort_values("cluster")

    genero = (
        base["Gênero - Como você se identifica?"]
        .fillna("Nao informado")
        .value_counts()
        .rename_axis("genero")
        .reset_index(name="registros")
    )
    genero["participacao"] = genero["registros"].apply(lambda x: pct(x, total_tratado))

    escolaridade = (
        base["Escolaridade"]
        .fillna("Nao informado")
        .value_counts()
        .rename_axis("escolaridade")
        .reset_index(name="registros")
    )
    escolaridade["participacao"] = escolaridade["registros"].apply(lambda x: pct(x, total_tratado))

    arquivo_entrega = base.copy()
    arquivo_entrega.insert(0, "id_registro", range(1, len(arquivo_entrega) + 1))
    colunas_remover = [
        "Nome Completo",
        "Email",
        "WhatsApp",
        "Endereço Completo",
    ]
    arquivo_entrega = arquivo_entrega.drop(columns=[c for c in colunas_remover if c in arquivo_entrega.columns])

    resumo = pd.DataFrame(
        [
            {"indicador": "Registros recebidos", "valor": total_original},
            {"indicador": "Registros com coordenadas", "valor": total_geocodificado},
            {"indicador": "Registros na base tratada", "valor": total_tratado},
            {"indicador": "Registros usados no mapa de calor", "valor": total_mapa},
            {"indicador": "Registros fora do recorte geografico", "valor": total_fora},
        ]
    )

    with pd.ExcelWriter(ARQUIVO_EXCEL_ENTREGA, engine="openpyxl") as writer:
        arquivo_entrega.to_excel(writer, sheet_name="dados_tratados", index=False)
        resumo.to_excel(writer, sheet_name="resumo", index=False)
        cluster_counts.to_excel(writer, sheet_name="clusters", index=False)
        genero.to_excel(writer, sheet_name="perfil_genero", index=False)
        escolaridade.to_excel(writer, sheet_name="perfil_escolaridade", index=False)
        fora_recorte.drop(columns=[c for c in colunas_remover if c in fora_recorte.columns]).to_excel(
            writer,
            sheet_name="fora_recorte",
            index=False,
        )

    data_geracao = datetime.now().strftime("%d/%m/%Y")
    maior_cluster = cluster_counts.sort_values("registros", ascending=False).iloc[0]

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relatório de Mapa de Calor e Distribuição Territorial</title>
  <style>
    :root {{
      --ink: #1f2937;
      --muted: #5b6472;
      --line: #d7dde6;
      --panel: #f7f9fc;
      --blue: #2457a6;
      --gold: #c98a14;
    }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.55;
      background: #ffffff;
    }}
    main {{
      max-width: 980px;
      margin: 0 auto;
      padding: 42px 28px 64px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      line-height: 1.15;
      color: #10233f;
    }}
    h2 {{
      margin: 34px 0 10px;
      padding-top: 4px;
      border-top: 1px solid var(--line);
      font-size: 20px;
      color: #10233f;
    }}
    h3 {{
      margin: 22px 0 8px;
      font-size: 16px;
      color: #10233f;
    }}
    p {{
      margin: 8px 0 12px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 28px;
    }}
    .summary {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--blue);
      border-radius: 8px;
      padding: 16px 18px;
    }}
    .summary ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      margin: 18px 0 8px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
    }}
    .card strong {{
      display: block;
      font-size: 22px;
      color: var(--blue);
    }}
    .card span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.25;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 18px;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 9px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: var(--panel);
      color: #10233f;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 110px 1fr 70px;
      align-items: center;
      gap: 10px;
      margin: 8px 0;
      font-size: 13px;
    }}
    .bar-track {{
      height: 16px;
      border-radius: 4px;
      background: #e9edf4;
      overflow: hidden;
    }}
    .bar-track span {{
      display: block;
      height: 100%;
      background: var(--blue);
    }}
    .bar-value {{
      text-align: right;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }}
    .note {{
      color: var(--muted);
      font-size: 13px;
    }}
    .callout {{
      border-left: 4px solid var(--gold);
      padding: 8px 0 8px 14px;
      color: #3a2a0a;
      background: #fff8e7;
    }}
    @media print {{
      main {{ padding: 24px; }}
      .cards {{ grid-template-columns: repeat(5, 1fr); }}
      a {{ color: inherit; text-decoration: none; }}
    }}
    @media (max-width: 780px) {{
      .cards {{ grid-template-columns: repeat(2, 1fr); }}
      .bar-row {{ grid-template-columns: 1fr; }}
      .bar-value {{ text-align: left; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Relatório de Mapa de Calor e Distribuição Territorial</h1>
  <div class="meta">
    Destinatário sugerido: Ministério do Empreendedorismo | Base analisada: inscrições georreferenciadas | Data de geração: {data_geracao}
  </div>

  <h2>Executive Summary</h2>
  <section class="summary">
    <ul>
      <li><strong>A base tratada está pronta para análise territorial.</strong> Dos {fmt_int(total_original)} registros recebidos, {fmt_int(total_geocodificado)} possuem latitude e longitude válidas, equivalente a {pct(total_geocodificado, total_original)} da base original.</li>
      <li><strong>O mapa de calor foi construído com {fmt_int(total_mapa)} registros no recorte principal.</strong> Esses pontos representam {pct(total_mapa, total_original)} do universo recebido e sustentam a leitura de concentração geográfica para planejamento de ações territoriais.</li>
      <li><strong>Foram identificados {fmt_int(total_fora)} registros fora do recorte geográfico esperado.</strong> Eles foram preservados para auditoria em planilha separada, sem contaminar o mapa e os clusters principais.</li>
      <li><strong>O maior agrupamento territorial concentra {fmt_int(maior_cluster['registros'])} registros.</strong> A clusterização oferece uma segmentação operacional para priorizar comunicação, logística, busca ativa e ações presenciais.</li>
    </ul>
  </section>

  <div class="cards">
    <div class="card"><strong>{fmt_int(total_original)}</strong><span>registros recebidos</span></div>
    <div class="card"><strong>{fmt_int(total_geocodificado)}</strong><span>com coordenadas</span></div>
    <div class="card"><strong>{fmt_int(total_tratado)}</strong><span>na base tratada</span></div>
    <div class="card"><strong>{fmt_int(total_mapa)}</strong><span>no mapa de calor</span></div>
    <div class="card"><strong>{fmt_int(total_fora)}</strong><span>fora do recorte</span></div>
  </div>

  <h2>A concentração territorial está pronta para orientar atuação local</h2>
  <p><strong>O mapa de calor deve ser usado como instrumento de priorização territorial, não como cadastro nominal.</strong> A versão interativa permite visualizar as áreas de maior concentração de inscrições georreferenciadas e alternar a camada de pontos para auditoria visual dos registros.</p>
  <p>Arquivo associado: <a href="{escape(ARQUIVO_MAPA)}">{escape(ARQUIVO_MAPA)}</a>.</p>

  <h3>Distribuição por cluster territorial</h3>
  <p>Os clusters foram recalculados apenas dentro do recorte geográfico principal para evitar que coordenadas distantes distorcessem os agrupamentos. Essa escolha torna os grupos mais úteis para planejamento operacional.</p>
  {barras_html(cluster_counts, "cluster", "registros", total=cluster_counts["registros"].max())}
  {tabela_html(cluster_counts.rename(columns={"cluster": "Cluster", "registros": "Registros", "participacao": "Participação"}))}

  <h2>Perfil da base tratada indica predominância de mulheres e público com ensino médio/superior</h2>
  <p><strong>O perfil declarado reforça o potencial de ações focalizadas de empreendedorismo, capacitação e formalização.</strong> As variáveis de gênero e escolaridade podem apoiar segmentação de linguagem, canais e desenho de trilhas formativas, desde que usadas de forma agregada e respeitando proteção de dados pessoais.</p>

  <h3>Perfil por gênero declarado</h3>
  {tabela_html(genero.head(10).rename(columns={"genero": "Gênero declarado", "registros": "Registros", "participacao": "Participação"}))}

  <h3>Perfil por escolaridade</h3>
  {tabela_html(escolaridade.head(10).rename(columns={"escolaridade": "Escolaridade", "registros": "Registros", "participacao": "Participação"}))}

  <h2>Recomendações para uso pelo Ministério</h2>
  <ol>
    <li><strong>Usar o mapa de calor para priorização territorial.</strong> Iniciar ações, visitas, parcerias ou campanhas digitais pelas regiões de maior densidade.</li>
    <li><strong>Usar os clusters como unidades operacionais.</strong> Cada cluster pode orientar rotas, agendas, mutirões de atendimento, eventos de capacitação e comunicação regionalizada.</li>
    <li><strong>Validar os registros fora do recorte antes de descartá-los.</strong> Parte pode representar erro de geocodificação; outra parte pode indicar inscrições realmente fora da região foco.</li>
    <li><strong>Compartilhar preferencialmente a base anonimizada.</strong> Para circulação institucional, utilizar o arquivo {escape(ARQUIVO_EXCEL_ENTREGA)}, que remove nome, e-mail, telefone e endereço completo.</li>
  </ol>

  <h2>Pontos que ainda merecem validação</h2>
  <p>Antes de usar a base para decisões finais de atendimento nominal, recomenda-se validar CEPs sem coordenadas, revisar os {fmt_int(total_fora)} registros fora do recorte e confirmar se o território de interesse é apenas Grande São Paulo ou se deve incluir outros municípios/estados.</p>

  <h2>Caveats e premissas</h2>
  <div class="callout">
    <p><strong>Geocodificação por CEP aproxima localização.</strong> As coordenadas representam uma referência geográfica associada ao CEP/endereço, não necessariamente o ponto exato de residência.</p>
    <p><strong>Dados pessoais foram removidos da base recomendada para entrega.</strong> O arquivo completo técnico permanece no projeto, mas a versão de entrega reduz risco de exposição indevida.</p>
    <p><strong>O mapa HTML depende de bibliotecas de mapa carregadas pela internet.</strong> Com conexão ativa, a camada de OpenStreetMap e o mapa de calor são renderizados normalmente no navegador.</p>
  </div>

  <p class="note">Arquivos de referência: {escape(ARQUIVO_BASE_TRATADA)} como base técnica completa; {escape(ARQUIVO_EXCEL_ENTREGA)} como base recomendada para compartilhamento; {escape(ARQUIVO_RELATORIO)} como relatório formal.</p>
</main>
</body>
</html>
"""

    Path(ARQUIVO_RELATORIO).write_text(html, encoding="utf-8")

    print(f"Arquivo principal tecnico: {ARQUIVO_BASE_TRATADA}")
    print(f"Arquivo recomendado para entrega: {ARQUIVO_EXCEL_ENTREGA}")
    print(f"Relatorio criado: {ARQUIVO_RELATORIO}")
    print(f"Registros no mapa: {total_mapa}")
    print(f"Registros fora do recorte: {total_fora}")


if __name__ == "__main__":
    main()
