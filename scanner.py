"""Componente: leitura de código de barras (ISBN) por câmera.

Usa streamlit-webrtc + pyzbar + opencv quando disponíveis. Em ambientes onde
essas bibliotecas não estão instaladas (ex.: Streamlit Cloud sem libzbar), faz
fallback elegante para o st.camera_input + pyzbar, e por fim para entrada manual.
"""
from __future__ import annotations

import streamlit as st

from components.utils import buscar_por_isbn, registrar_consulta

# Detecta dependências disponíveis sem quebrar o app
try:
    from pyzbar.pyzbar import decode as _zbar_decode
    import numpy as np
    from PIL import Image
    _PYZBAR_OK = True
except Exception:  # noqa: BLE001
    _PYZBAR_OK = False

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    import av  # noqa: F401
    _WEBRTC_OK = True
except Exception:  # noqa: BLE001
    _WEBRTC_OK = False


def _decodificar_imagem(imagem) -> str | None:
    """Decodifica códigos de barras de uma imagem PIL. Retorna o ISBN ou None."""
    if not _PYZBAR_OK:
        return None
    arr = np.array(imagem.convert("RGB"))
    for codigo in _zbar_decode(arr):
        dado = codigo.data.decode("utf-8")
        # ISBN-13 começa com 978/979; aceita também ISBN-10
        if dado.isdigit() and len(dado) in (10, 13):
            return dado
    return None


def _processar_isbn(livros: list[dict], isbn: str) -> None:
    """Busca o livro pelo ISBN e seleciona, ou avisa que não foi encontrado."""
    livro = buscar_por_isbn(livros, isbn)
    if livro:
        registrar_consulta(livro)
        st.session_state.livro_selecionado = livro
        st.success(f"Livro encontrado: {livro['titulo']}")
        st.rerun()
    else:
        st.warning(f"Nenhum livro cadastrado com o ISBN {isbn}.")


def render_scanner(livros: list[dict]) -> None:
    """Renderiza o scanner de código de barras com fallbacks."""
    st.markdown("#### Scanner de Código de Barras")

    if not _PYZBAR_OK:
        st.info(
            "A leitura automática requer as bibliotecas `pyzbar`, `opencv-python` "
            "e a lib de sistema `libzbar0`. Use a entrada manual de ISBN abaixo."
        )

    # --- Modo 1: webcam ao vivo (webrtc) ---
    if _WEBRTC_OK and _PYZBAR_OK:
        st.caption("Modo ao vivo: aponte o código de barras para a câmera.")
        ctx = webrtc_streamer(
            key="scanner-webrtc",
            mode=WebRtcMode.SENDONLY,
            media_stream_constraints={"video": True, "audio": False},
            video_receiver_size=1,
        )
        if ctx.video_receiver:
            try:
                frame = ctx.video_receiver.get_frame(timeout=1)
                img = frame.to_image()
                isbn = _decodificar_imagem(img)
                if isbn:
                    _processar_isbn(livros, isbn)
            except Exception:  # noqa: BLE001
                pass

    # --- Modo 2: foto da câmera (mobile-friendly) ---
    if _PYZBAR_OK:
        foto = st.camera_input("Ou tire uma foto do código de barras",
                               key="scanner-photo")
        if foto is not None:
            img = Image.open(foto)
            isbn = _decodificar_imagem(img)
            if isbn:
                _processar_isbn(livros, isbn)
            else:
                st.warning("Nenhum código de barras detectado. Tente novamente.")

    # --- Modo 3: entrada manual (sempre disponível) ---
    st.markdown("##### Digitar ISBN manualmente")
    col_in, col_btn = st.columns([3, 1])
    with col_in:
        isbn_manual = st.text_input(
            "ISBN",
            placeholder="978...",
            label_visibility="collapsed",
            key="isbn_manual",
        )
    with col_btn:
        if st.button("Buscar", use_container_width=True, key="btn_isbn_manual"):
            if isbn_manual.strip():
                _processar_isbn(livros, isbn_manual.strip())
            else:
                st.warning("Informe um ISBN.")
