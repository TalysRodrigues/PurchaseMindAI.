"""
Página: Dashboard.

Regra de arquitetura: busca dados via services/, desenha via components/.
Nunca acessa database/ diretamente.
"""

import streamlit as st

from components.compra_card import render_compra_card
from components.notificacoes_widget import render_notificacoes
from config.constants import StatusCompra
from services import compras_service, notificacoes_service


def render() -> None:
    st.header("📊 Dashboard")

    # Verifica atrasos toda vez que o dashboard carrega e dispara notificações.
    try:
        compras_service.verificar_atrasos()
    except Exception as erro:
        st.warning(f"Não foi possível verificar atrasos agora: {erro}")

    try:
        compras = compras_service.listar_compras()
    except Exception as erro:
        st.error(f"Não foi possível carregar as compras: {erro}")
        compras = []

    # --- Indicadores -----------------------------------------------------
    total = len(compras)
    por_status = {s: 0 for s in StatusCompra}
    for c in compras:
        por_status[StatusCompra(c["status"])] += 1

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", total)
    col2.metric("Pendentes", por_status[StatusCompra.PENDENTE])
    col3.metric("Em trânsito", por_status[StatusCompra.EM_TRANSITO])
    col4.metric("Entregues", por_status[StatusCompra.ENTREGUE])
    col5.metric("Canceladas", por_status[StatusCompra.CANCELADA])

    st.divider()

    # --- Notificações ------------------------------------------------------
    st.subheader("🔔 Notificações")
    try:
        notificacoes = notificacoes_service.listar_pendentes()
    except Exception as erro:
        st.warning(f"Não foi possível carregar notificações: {erro}")
        notificacoes = []

    def _marcar_lida(notificacao_id: str) -> None:
        notificacoes_service.marcar_como_lida(notificacao_id)
        st.rerun()

    render_notificacoes(notificacoes, on_marcar_lida=_marcar_lida)

    st.divider()

    # --- Compras em andamento ----------------------------------------------
    st.subheader("Compras em andamento")
    em_andamento = [
        c for c in compras
        if c["status"] not in (StatusCompra.ENTREGUE.value, StatusCompra.CANCELADA.value)
    ]

    if not em_andamento:
        st.caption("Nenhuma compra em andamento no momento.")
    else:
        for compra in em_andamento:
            render_compra_card(compra)
