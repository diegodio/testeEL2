"""Entrelinhas — Análise Inteligente de Conteúdo e Classificação Indicativa.

Aplicação Streamlit para descobrir a classificação indicativa recomendada de
livros via leitura de ISBN, pesquisa textual e consulta ao acervo cadastrado.
"""
from __future__ import annotations

from collections import Counter

import streamlit as st

from components.book_card import render_book_card
from components.classification_card import render_classification
from components.dashboard import render_dashboard
from components.scanner import render_scanner
from components.search import render_search
from components.utils import (FAIXAS, carregar_css, carregar_livros,
                              init_state, registrar_consulta)

# ----------------------------- Configuração -----------------------------
st.set_page_config(
    page_title="Entrelinhas",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded",
)


def render_estatisticas(livros: list[dict]) -> None:
    """Renderiza os cards de estatísticas rápidas da página inicial."""
    total = len(livros)
    faixas = [lv.get("classificacao", {}).get("faixa_etaria", "—") for lv in livros]
    mais_comum = Counter(faixas).most_common(1)[0][0] if faixas else "—"

    infantis = sum(1 for f in faixas if f in ("Livre", "10 anos", "12 anos"))
    adultos = sum(1 for f in faixas if f in ("16 anos", "18 anos"))

    cards = [
        (str(total), "Livros analisados"),
        (mais_comum, "Faixa mais comum"),
        (str(infantis), "Livros infantojuvenis"),
        (str(adultos), "Livros adultos"),
    ]

    cols = st.columns(4)
    for col, (valor, label) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-value">{valor}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_home(livros: list[dict]) -> None:
    """Página inicial."""
    st.markdown('<div class="brand-title">Entrelinhas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-subtitle">Análise Inteligente de Conteúdo e '
        'Classificação Indicativa</div>',
        unsafe_allow_html=True,
    )

    render_estatisticas(livros)
    st.write("")
    st.divider()

    # Busca rápida na home
    render_search(livros)

    st.divider()

    # Livros recentes (por consultas registradas no acervo)
    st.markdown("#### Livros Recentes")
    recentes = sorted(livros, key=lambda lv: lv.get("consultas", 0), reverse=True)[:4]
    for livro in recentes:
        if render_book_card(livro, key_prefix="home"):
            registrar_consulta(livro)
            st.session_state.livro_selecionado = livro
            st.rerun()


def render_favoritos(livros: list[dict]) -> None:
    """Página de favoritos."""
    st.markdown("#### Favoritos")
    favs = [lv for lv in livros if lv.get("isbn") in st.session_state.favoritos]
    if not favs:
        st.info("Nenhum livro favoritado ainda. Use ☆ na tela de análise.")
        return
    for livro in favs:
        if render_book_card(livro, key_prefix="fav"):
            registrar_consulta(livro)
            st.session_state.livro_selecionado = livro
            st.rerun()


def main() -> None:
    carregar_css()
    init_state()
    livros = carregar_livros()

    # ----------------------------- Sidebar -----------------------------
    with st.sidebar:
        st.markdown("### 📖 Entrelinhas")
        pagina = st.radio(
            "Navegação",
            ["Início", "Pesquisar", "Scanner", "Favoritos", "Dashboard"],
            label_visibility="collapsed",
        )

        # Histórico de pesquisas
        if st.session_state.historico:
            st.divider()
            st.markdown("**Histórico**")
            for h in reversed(st.session_state.historico[-8:]):
                st.caption(f"· {h}")

    # ------------------- Resultado tem prioridade -------------------
    if st.session_state.livro_selecionado is not None:
        if st.button("← Voltar"):
            st.session_state.livro_selecionado = None
            st.rerun()
        st.divider()
        render_classification(st.session_state.livro_selecionado)
        return

    # ----------------------------- Páginas -----------------------------
    if pagina == "Início":
        render_home(livros)
    elif pagina == "Pesquisar":
        st.markdown("#### Pesquisar Livros")
        render_search(livros)
    elif pagina == "Scanner":
        render_scanner(livros)
    elif pagina == "Favoritos":
        render_favoritos(livros)
    elif pagina == "Dashboard":
        render_dashboard(livros)


if __name__ == "__main__":
    main()
