"""
Página: Timeline de uma compra específica.
"""

import streamlit as st

from components.status_badge import render_status_badge
from config.constants import StatusCompra
from services import compras_service
from services.compras_service import TransicaoInvalidaError, ErroValidacao


def render() -> None:
    st.header("🕒 Timeline")

    try:
        compras = compras_service.listar_compras()
    except Exception as erro:
        st.error(f"Não foi possível carregar as compras: {erro}")
        return

    if not compras:
        st.caption("Nenhuma compra cadastrada ainda.")
        return

    opcoes = {f"{c['descricao']} ({c['status']})": c["id"] for c in compras}
    escolha = st.selectbox("Selecione a compra", options=list(opcoes.keys()))
    compra_id = opcoes[escolha]

    compra = next(c for c in compras if c["id"] == compra_id)
    status_atual = StatusCompra(compra["status"])

    st.subheader(compra["descricao"])
    render_status_badge(status_atual)

    st.divider()

    # --- Ação: avançar status ------------------------------------------------
    from services.compras_service import TRANSICOES_VALIDAS

    proximos = TRANSICOES_VALIDAS[status_atual]
    if proximos:
        col_select, col_botao = st.columns([3, 1])
        with col_select:
            opcoes_status = {s.label: s for s in proximos}
            proximo_label = st.selectbox("Mudar status para", options=list(opcoes_status.keys()))
        with col_botao:
            st.write("")
            st.write("")
            if st.button("Confirmar mudança"):
                try:
                    compras_service.mudar_status(compra_id, opcoes_status[proximo_label])
                    st.success("Status atualizado!")
                    st.rerun()
                except (TransicaoInvalidaError, ErroValidacao) as erro:
                    st.error(str(erro))
    else:
        st.caption("Este é um status final — não há mais transições possíveis.")

    st.divider()

    # --- Histórico -------------------------------------------------------
    st.subheader("Histórico de eventos")
    historico = compras_service.obter_timeline(compra_id)

    if not historico:
        st.caption("Sem eventos registrados.")
        return

    for evento in historico:
        de = StatusCompra(evento["status_anterior"]).label if evento["status_anterior"] else "—"
        para = StatusCompra(evento["status_novo"]).label
        linha = f"**{de} → {para}**"
        if evento.get("observacao"):
            linha += f" — {evento['observacao']}"
        st.write(linha)
