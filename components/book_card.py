"""Componente: card de livro para listagens."""
from __future__ import annotations

import streamlit as st

from components.utils import cor_da_faixa


def render_book_card(livro: dict, key_prefix: str = "") -> bool:
    """Renderiza um card compacto de livro. Retorna True se o usuário clicar."""
    faixa = livro.get("classificacao", {}).get("faixa_etaria", "—")
    cor = cor_da_faixa(faixa)
    isbn = livro.get("isbn", "")

    col_info, col_seal, col_btn = st.columns([5, 1.4, 1.3])

    with col_info:
        st.markdown(
            f"""
            <div class="book-card">
                <div class="book-title">{livro.get('titulo', '')}</div>
                <div class="book-author">{livro.get('autor', '')} · {livro.get('editora', '')} · {livro.get('ano', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_seal:
        st.markdown(
            f"""
            <div style="background:{cor};color:white;border-radius:12px;
                 padding:0.6rem 0.2rem;text-align:center;font-weight:700;
                 font-size:0.85rem;margin-top:0.15rem;">{faixa}</div>
            """,
            unsafe_allow_html=True,
        )

    with col_btn:
        clicado = st.button("Analisar", key=f"{key_prefix}_btn_{isbn}",
                            use_container_width=True)

    return clicado
