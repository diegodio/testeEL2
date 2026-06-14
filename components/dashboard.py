"""Componente: dashboard administrativo com gráficos interativos (Plotly)."""
from __future__ import annotations

from collections import Counter

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.utils import COR_FAIXA, FAIXAS, CRITERIOS, cor_da_faixa


def render_dashboard(livros: list[dict]) -> None:
    """Renderiza o dashboard com métricas e gráficos."""
    st.markdown("#### Dashboard Administrativo")

    if not livros:
        st.info("Nenhum livro cadastrado.")
        return

    # Métricas-chave
    consultas_sessao = st.session_state.get("consultas", {})
    total = len(livros)
    total_consultas = sum(lv.get("consultas", 0) for lv in livros) + sum(consultas_sessao.values())

    c1, c2, c3 = st.columns(3)
    c1.metric("Livros cadastrados", total)
    c2.metric("Total de consultas", total_consultas)
    c3.metric("Favoritos", len(st.session_state.get("favoritos", set())))

    st.write("")

    # ---------- Distribuição por faixa etária ----------
    contagem = Counter(lv.get("classificacao", {}).get("faixa_etaria", "—")
                       for lv in livros)
    faixas_ord = [f for f in FAIXAS if f in contagem]
    valores = [contagem[f] for f in faixas_ord]
    cores = [COR_FAIXA[f] for f in faixas_ord]

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_bar = go.Figure(
            go.Bar(x=faixas_ord, y=valores, marker_color=cores,
                   text=valores, textposition="outside")
        )
        fig_bar.update_layout(
            title="Distribuição por Faixa Etária",
            margin=dict(l=10, r=10, t=40, b=10),
            height=320, plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        fig_pie = go.Figure(
            go.Pie(labels=faixas_ord, values=valores,
                   marker=dict(colors=cores), hole=0.55)
        )
        fig_pie.update_layout(
            title="Proporção por Faixa",
            margin=dict(l=10, r=10, t=40, b=10),
            height=320, paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---------- Livros mais consultados ----------
    st.markdown("##### Livros Mais Consultados")
    ranking = sorted(
        livros,
        key=lambda lv: lv.get("consultas", 0) + consultas_sessao.get(lv.get("isbn"), 0),
        reverse=True,
    )[:8]
    titulos = [lv["titulo"] for lv in ranking][::-1]
    consultas = [lv.get("consultas", 0) + consultas_sessao.get(lv.get("isbn"), 0)
                 for lv in ranking][::-1]
    cores_rank = [cor_da_faixa(lv.get("classificacao", {}).get("faixa_etaria"))
                  for lv in ranking][::-1]

    fig_rank = go.Figure(
        go.Bar(x=consultas, y=titulos, orientation="h",
               marker_color=cores_rank, text=consultas, textposition="outside")
    )
    fig_rank.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=360,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    # ---------- Mapa de calor de critérios ----------
    st.markdown("##### Intensidade Média por Critério")
    escala = {"Inexistente": 0, "Leve": 1, "Moderado": 2, "Moderada": 2,
              "Intenso": 3, "Intensa": 3}
    medias = {}
    for chave, rotulo in CRITERIOS.items():
        vals = [escala.get(lv.get("classificacao", {}).get(chave, ""), 0)
                for lv in livros]
        medias[rotulo] = sum(vals) / len(vals) if vals else 0

    fig_crit = px.bar(
        x=list(medias.keys()), y=list(medias.values()),
        color=list(medias.values()), color_continuous_scale="Blues",
        labels={"x": "", "y": "Intensidade média (0–3)"},
    )
    fig_crit.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=320,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_crit, use_container_width=True)
