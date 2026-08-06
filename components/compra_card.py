"""
Cartão de exibição de uma ordem de compra (usado no Dashboard e no Histórico).

Regra de arquitetura: recebe os dados já prontos (dict, com os itens
embutidos em compra["compra_itens"]) e um callback opcional para ações.
Não busca dados sozinho, não chama services/ nem database/ diretamente.
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
    Desenha um cartão com título, itens, status e prazo de uma ordem de compra.
    Se `on_ver_timeline` for informado, mostra um botão "Ver timeline".
    """
    status = StatusCompra(compra["status"])
    itens = compra.get("compra_itens") or []
    quantidade_total = sum(item["quantidade"] for item in itens)

    with st.container(border=True):
        col_info, col_status = st.columns([4, 1])

        with col_info:
            st.markdown(f"**{compra['titulo']}**")

            detalhes = (
                f"{len(itens)} item(ns) · {quantidade_total} unidade(s) no total · "
                f"Prazo: {formatar_data_br(compra.get('prazo_entrega'))}"
            )
            if compra.get("criado_por"):
                detalhes += f" · Cadastrado por: {compra['criado_por']}"
            st.caption(detalhes)

            if itens:
                with st.expander("Ver itens"):
                    for item in itens:
                        st.write(f"- {item['descricao']} — {item['quantidade']} unidade(s)")

        with col_status:
            render_status_badge(status)

        if on_ver_timeline is not None:
            if st.button("Ver timeline", key=f"timeline_{compra['id']}"):
                on_ver_timeline(compra["id"])
