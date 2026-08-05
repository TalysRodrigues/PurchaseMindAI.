"""
Badge visual de status de compra.

Regra de arquitetura: componente de UI puro — recebe um StatusCompra e
desenha. Não acessa banco nem services.
"""

import streamlit as st

from config.constants import StatusCompra

# Cor de fundo de cada status (hex), usada no badge.
_CORES: dict[StatusCompra, str] = {
    StatusCompra.PENDENTE: "#94a3b8",     # cinza
    StatusCompra.APROVADA: "#3b82f6",     # azul
    StatusCompra.EM_TRANSITO: "#f59e0b",  # laranja
    StatusCompra.ENTREGUE: "#22c55e",     # verde
    StatusCompra.CANCELADA: "#ef4444",    # vermelho
}


def cor_do_status(status: StatusCompra) -> str:
    """Retorna a cor hex associada a um status. Função pura, testável sem UI."""
    return _CORES[status]


def render_status_badge(status: StatusCompra) -> None:
    """Desenha um badge colorido com ícone + texto do status."""
    cor = cor_do_status(status)
    st.markdown(
        f"""
        <span style="
            background-color:{cor};
            color:white;
            padding:2px 10px;
            border-radius:12px;
            font-size:0.85em;
            font-weight:600;
            white-space:nowrap;
        ">
            {status.icone} {status.label}
        </span>
        """,
        unsafe_allow_html=True,
    )
