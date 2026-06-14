"""Utilidades compartilhadas: carregamento de dados, cache, busca fuzzy e cores."""
from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "livros.json"

# Ordem etária canônica (do mais livre ao mais restrito)
FAIXAS = ["Livre", "10 anos", "12 anos", "14 anos", "16 anos", "18 anos"]

# Cores do selo por faixa (sistema semelhante ao ClassInd brasileiro)
COR_FAIXA: dict[str, str] = {
    "Livre": "#2ecc71",
    "10 anos": "#3498db",
    "12 anos": "#f1c40f",
    "14 anos": "#e67e22",
    "16 anos": "#e74c3c",
    "18 anos": "#1a1a1a",
}

# Critérios avaliados (chave no JSON -> rótulo legível)
CRITERIOS: dict[str, str] = {
    "violencia": "Violência",
    "linguagem_impropria": "Linguagem Imprópria",
    "sexo_nudez": "Sexo e Nudez",
    "drogas": "Drogas",
    "medo_tensao": "Medo e Tensão",
}

# Cor por nível de intensidade
COR_NIVEL: dict[str, str] = {
    "Inexistente": "#2ecc71",
    "Leve": "#3498db",
    "Moderado": "#e67e22",
    "Moderada": "#e67e22",
    "Intenso": "#e74c3c",
    "Intensa": "#e74c3c",
}


@st.cache_data(show_spinner=False)
def carregar_livros() -> list[dict[str, Any]]:
    """Carrega os livros do JSON com cache inteligente."""
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado em {DATA_PATH}")
        return []
    except json.JSONDecodeError as exc:
        st.error(f"Erro ao ler livros.json: {exc}")
        return []


def buscar_por_isbn(livros: list[dict], isbn: str) -> dict | None:
    """Busca exata por ISBN (ignora hifens e espaços)."""
    alvo = isbn.replace("-", "").replace(" ", "").strip()
    for livro in livros:
        if livro.get("isbn", "").replace("-", "").strip() == alvo:
            return livro
    return None


def _similaridade(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def busca_fuzzy(livros: list[dict], termo: str, limite: float = 0.35) -> list[dict]:
    """Busca instantânea e tolerante a erros em título, autor, ISBN e editora."""
    termo = termo.strip()
    if not termo:
        return livros

    termo_l = termo.lower()
    resultados: list[tuple[float, dict]] = []

    for livro in livros:
        campos = [
            livro.get("titulo", ""),
            livro.get("autor", ""),
            livro.get("editora", ""),
            livro.get("isbn", ""),
            livro.get("genero", ""),
        ]
        melhor = 0.0
        for campo in campos:
            campo_l = campo.lower()
            if termo_l in campo_l:  # substring → prioridade máxima
                melhor = max(melhor, 1.0)
            else:
                melhor = max(melhor, _similaridade(termo, campo))
        if melhor >= limite:
            resultados.append((melhor, livro))

    resultados.sort(key=lambda x: x[0], reverse=True)
    return [livro for _, livro in resultados]


def cor_da_faixa(faixa: str) -> str:
    return COR_FAIXA.get(faixa, "#888888")


def cor_do_nivel(nivel: str) -> str:
    return COR_NIVEL.get(nivel, "#888888")


def carregar_css() -> None:
    """Injeta o CSS customizado."""
    css_path = Path(__file__).resolve().parent.parent / "styles" / "custom.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                    unsafe_allow_html=True)


def init_state() -> None:
    """Inicializa o estado de sessão (favoritos, histórico, livro selecionado)."""
    st.session_state.setdefault("favoritos", set())
    st.session_state.setdefault("historico", [])
    st.session_state.setdefault("livro_selecionado", None)
    st.session_state.setdefault("consultas", {})  # isbn -> contagem na sessão


def registrar_consulta(livro: dict) -> None:
    """Registra histórico e contagem de consultas."""
    isbn = livro.get("isbn", "")
    titulo = livro.get("titulo", "")
    if titulo and (not st.session_state.historico
                   or st.session_state.historico[-1] != titulo):
        st.session_state.historico.append(titulo)
        st.session_state.historico = st.session_state.historico[-20:]
    st.session_state.consultas[isbn] = st.session_state.consultas.get(isbn, 0) + 1
