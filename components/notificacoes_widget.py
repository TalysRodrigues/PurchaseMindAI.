"""
Widget de exibição de notificações pendentes.

Regra de arquitetura: recebe a lista já carregada e um callback para
marcar como lida. Não acessa banco nem services/ diretamente.
"""

from typing import Any, Callable

import streamlit as st

_ICONE_POR_TIPO: dict[str, str] = {
    "nova_compra": "🆕",
    "mudanca_status": "🔄",
    "atraso_entrega": "⚠️",
    "entrega_concluida": "📦",
}


def render_notificacoes(
    notificacoes: list[dict[str, Any]],
    on_marcar_lida: Callable[[str], None],
) -> None:
    """Desenha a lista de notificações não lidas, com botão de marcar como lida."""
    if not notificacoes:
        st.caption("Nenhuma notificação pendente. 🎉")
        return

    for notificacao in notificacoes:
        icone = _ICONE_POR_TIPO.get(notificacao["tipo"], "🔔")
        col_msg, col_acao = st.columns([5, 1])

        with col_msg:
            st.write(f"{icone} {notificacao['mensagem']}")

        with col_acao:
            if st.button("OK", key=f"notif_{notificacao['id']}"):
                on_marcar_lida(notificacao["id"])
