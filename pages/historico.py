"""
Página: Histórico completo de compras, com filtro por status.
"""

import streamlit as st

from components.compra_card import render_compra_card
from config.constants import StatusCompra
from services import compras_service


def render() -> None:
    st.header("📚 Histórico")

    opcoes_filtro = {"Todos": None}
    opcoes_filtro.update({s.label: s for s in StatusCompra})

    filtro_label = st.selectbox("Filtrar por status", options=list(opcoes_filtro.keys()))
    status_filtro = opcoes_filtro[filtro_label]

    try:
        compras = compras_service.listar_compras(status=status_filtro)
    except Exception as erro:
        st.error(f"Não foi possível carregar as compras: {erro}")
        return

    if not compras:
        st.caption("Nenhuma compra encontrada com esse filtro.")
        return

    st.caption(f"{len(compras)} compra(s) encontrada(s)")

    for compra in compras:
        render_compra_card(compra)
