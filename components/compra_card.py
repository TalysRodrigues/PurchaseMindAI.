"""
Cartão de exibição de uma compra (usado no Dashboard e no Histórico).

Regra de arquitetura: recebe os dados já prontos (dict) e um callback
opcional para ações. Não busca dados sozinho, não chama services/ nem
database/ diretamente — quem faz isso é pages/.
"""

from typing import Any, Callable, Optional

import streamlit as st

from components.status_badge import render_status_badge
from config.constants import StatusCompra
from utils.formatters import formatar_data_br


def render_compra_card(
    compra: dict[str, Any],
    on_ver_timeline: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Desenha um cartão com descrição, quantidade, status e prazo de uma compra.
    Se `on_ver_timeline` for informado, mostra um botão "Ver timeline".
    """
    status = StatusCompra(compra["status"])

    with st.container(border=True):
        col_info, col_status = st.columns([4, 1])

        with col_info:
            st.markdown(f"**{compra['descricao']}**")
            st.caption(
                f"Quantidade: {compra['quantidade']} · "
                f"Prazo: {formatar_data_br(compra.get('prazo_entrega'))}"
            )

        with col_status:
            render_status_badge(status)

        if on_ver_timeline is not None:
            if st.button("Ver timeline", key=f"timeline_{compra['id']}"):
                on_ver_timeline(compra["id"])
