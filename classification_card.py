"""Componente: tela completa de resultado da classificação indicativa."""
from __future__ import annotations

import streamlit as st

from components.utils import CRITERIOS, cor_da_faixa, cor_do_nivel


def _capa_placeholder(titulo: str, cor: str) -> str:
    """Gera um placeholder de capa estilizado quando não há imagem."""
    inicial = (titulo[:1] or "?").upper()
    return f"""
        <div style="background:linear-gradient(135deg,{cor},{cor}cc);
             border-radius:14px;width:100%;aspect-ratio:2/3;display:flex;
             align-items:center;justify-content:center;color:white;
             font-size:3rem;font-weight:700;box-shadow:0 8px 24px rgba(0,0,0,0.15);">
            {inicial}
        </div>
    """


def render_classification(livro: dict) -> None:
    """Renderiza a análise completa de classificação indicativa."""
    cls = livro.get("classificacao", {})
    faixa = cls.get("faixa_etaria", "—")
    cor = cor_da_faixa(faixa)

    # ---------- Cabeçalho ----------
    col_capa, col_info = st.columns([1, 3])
    with col_capa:
        capa = livro.get("capa", "")
        if capa:
            st.image(capa, use_container_width=True)
        else:
            st.markdown(_capa_placeholder(livro.get("titulo", ""), cor),
                        unsafe_allow_html=True)

    with col_info:
        st.markdown(f"### {livro.get('titulo', '')}")
        st.markdown(
            f"**{livro.get('autor', '')}**  \n"
            f"{livro.get('editora', '')} · {livro.get('ano', '')}  \n"
            f"ISBN: `{livro.get('isbn', '')}`  \n"
            f"Gênero: {livro.get('genero', '—')}"
        )
        # Selo em destaque
        st.markdown(
            f"""
            <div style="margin-top:0.8rem;">
                <span class="rating-seal" style="background:{cor};">{faixa}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ---------- Resumo Executivo ----------
    st.markdown("#### Resumo Executivo")
    st.markdown(cls.get("descricao", "—"))

    # ---------- Temas Sensíveis ----------
    temas = cls.get("temas_sensiveis", [])
    if temas:
        st.markdown("#### Temas Sensíveis")
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in temas)
        st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
    st.write("")

    # ---------- Avaliação Completa ----------
    st.markdown("#### Avaliação Completa")
    for chave, rotulo in CRITERIOS.items():
        nivel = cls.get(chave, "—")
        cor_n = cor_do_nivel(nivel)
        st.markdown(
            f"""
            <div class="criterion">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="criterion-name">{rotulo}</span>
                    <span class="criterion-level" style="color:{cor_n};">{nivel}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Justificativa geral
    st.markdown("#### Justificativa")
    st.info(cls.get("justificativa", "—"))

    # ---------- Recomendações ----------
    recs = cls.get("recomendacoes", [])
    if recs:
        st.markdown("#### Recomendações")
        for r in recs:
            st.markdown(f"- {r}")

    st.divider()

    # ---------- Ações: favoritar, exportar, compartilhar ----------
    col_a, col_b, col_c = st.columns(3)
    isbn = livro.get("isbn", "")

    with col_a:
        favorito = isbn in st.session_state.favoritos
        label = "★ Favoritado" if favorito else "☆ Favoritar"
        if st.button(label, use_container_width=True, key=f"fav_{isbn}"):
            if favorito:
                st.session_state.favoritos.discard(isbn)
            else:
                st.session_state.favoritos.add(isbn)
            st.rerun()

    with col_b:
        pdf_bytes = _gerar_pdf(livro)
        st.download_button(
            "⬇ Exportar PDF",
            data=pdf_bytes,
            file_name=f"analise_{isbn}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_{isbn}",
        )

    with col_c:
        if st.button("⧉ Compartilhar", use_container_width=True, key=f"share_{isbn}"):
            st.code(_texto_compartilhavel(livro), language=None)


def _texto_compartilhavel(livro: dict) -> str:
    cls = livro.get("classificacao", {})
    return (
        f"📚 {livro.get('titulo')} — {livro.get('autor')}\n"
        f"Classificação Entrelinhas: {cls.get('faixa_etaria')}\n"
        f"{cls.get('descricao')}\n"
        f"Temas: {', '.join(cls.get('temas_sensiveis', [])) or 'nenhum'}"
    )


def _gerar_pdf(livro: dict) -> bytes:
    """Gera um PDF da análise usando reportlab."""
    from io import BytesIO

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)
    from reportlab.lib import colors

    cls = livro.get("classificacao", {})
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("T", parent=styles["Title"], fontSize=18)
    h_style = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12,
                             spaceBefore=12)
    body = styles["BodyText"]

    elems = [
        Paragraph("Entrelinhas — Análise de Classificação Indicativa", titulo_style),
        Spacer(1, 0.4 * cm),
        Paragraph(f"<b>{livro.get('titulo')}</b>", styles["Heading1"]),
        Paragraph(f"{livro.get('autor')} · {livro.get('editora')} · {livro.get('ano')}", body),
        Paragraph(f"ISBN: {livro.get('isbn')}", body),
        Spacer(1, 0.3 * cm),
        Paragraph(f"<b>Faixa etária recomendada: {cls.get('faixa_etaria')}</b>", styles["Heading2"]),
        Paragraph("Resumo Executivo", h_style),
        Paragraph(cls.get("descricao", "—"), body),
        Paragraph("Temas Sensíveis", h_style),
        Paragraph(", ".join(cls.get("temas_sensiveis", [])) or "Nenhum", body),
        Paragraph("Avaliação Completa", h_style),
    ]

    dados = [["Critério", "Nível"]]
    for chave, rotulo in CRITERIOS.items():
        dados.append([rotulo, cls.get(chave, "—")])
    tabela = Table(dados, colWidths=[8 * cm, 6 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a84ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f7")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elems.append(tabela)

    elems += [
        Paragraph("Justificativa", h_style),
        Paragraph(cls.get("justificativa", "—"), body),
        Paragraph("Recomendações", h_style),
    ]
    for r in cls.get("recomendacoes", []):
        elems.append(Paragraph(f"• {r}", body))

    doc.build(elems)
    return buffer.getvalue()
