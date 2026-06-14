"""Componente: pesquisa instantânea com busca fuzzy, filtros e paginação."""
from __future__ import annotations

import streamlit as st

from components.book_card import render_book_card
from components.utils import (FAIXAS, busca_fuzzy, registrar_consulta)


def render_search(livros: list[dict]) -> None:
    """Renderiza a interface de pesquisa com filtros e paginação."""
    termo = st.text_input(
        "Pesquisar",
        placeholder="Título, autor, ISBN, editora ou palavra-chave…",
        label_visibility="collapsed",
        key="busca_global",
    )

    # ---------- Filtros ----------
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        faixas_sel = st.multiselect(
            "Filtrar por faixa etária",
            options=FAIXAS,
            placeholder="Todas as faixas",
        )
    with col_f2:
        generos = sorted({lv.get("genero", "—") for lv in livros})
        generos_sel = st.multiselect(
            "Filtrar por gênero",
            options=generos,
            placeholder="Todos os gêneros",
        )

    # ---------- Aplicar busca + filtros ----------
    resultados = busca_fuzzy(livros, termo)
    if faixas_sel:
        resultados = [lv for lv in resultados
                      if lv.get("classificacao", {}).get("faixa_etaria") in faixas_sel]
    if generos_sel:
        resultados = [lv for lv in resultados if lv.get("genero") in generos_sel]

    st.caption(f"{len(resultados)} livro(s) encontrado(s)")

    # ---------- Paginação ----------
    POR_PAGINA = 6
    total_paginas = max(1, (len(resultados) + POR_PAGINA - 1) // POR_PAGINA)
    pagina = st.session_state.get("pagina_busca", 1)
    pagina = min(pagina, total_paginas)

    inicio = (pagina - 1) * POR_PAGINA
    pagina_itens = resultados[inicio:inicio + POR_PAGINA]

    for livro in pagina_itens:
        if render_book_card(livro, key_prefix="busca"):
            registrar_consulta(livro)
            st.session_state.livro_selecionado = livro
            st.rerun()

    # Controles de paginação
    if total_paginas > 1:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("← Anterior", disabled=pagina <= 1, use_container_width=True):
                st.session_state.pagina_busca = pagina - 1
                st.rerun()
        with c2:
            st.markdown(
                f"<div style='text-align:center;opacity:0.6;margin-top:0.4rem;'>"
                f"Página {pagina} de {total_paginas}</div>",
                unsafe_allow_html=True,
            )
        with c3:
            if st.button("Próxima →", disabled=pagina >= total_paginas,
                         use_container_width=True):
                st.session_state.pagina_busca = pagina + 1
                st.rerun()
