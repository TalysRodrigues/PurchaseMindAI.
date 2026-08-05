"""
PurchaseMind AI - Ponto de entrada da aplicação.

Regra de arquitetura: este arquivo APENAS inicializa o sistema
(configuração de página, estado de sessão e roteamento entre seções).
Nenhuma regra de negócio deve ser implementada aqui — isso pertence a services/.
Nenhum acesso a banco deve ser feito aqui — isso pertence a database/.
"""

import streamlit as st

from config.settings import settings
from pages import dashboard, cadastro, timeline, historico, chat_ia, fornecedores

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon=settings.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.logo("assets/logo.png")

# ---------------------------------------------------------------------------
# Estado de sessão
# ---------------------------------------------------------------------------
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Dashboard"


# ---------------------------------------------------------------------------
# Navegação (sidebar)
# ---------------------------------------------------------------------------
PAGINAS = {
    "Dashboard": "📊",
    "Cadastro": "📝",
    "Timeline": "🕒",
    "Histórico": "📚",
    "Chat IA": "💬",
    "Fornecedores": "🚚",
}


def render_sidebar() -> str:
    """Renderiza o menu lateral e retorna a página selecionada."""
    with st.sidebar:
        st.title(f"{settings.APP_ICON} {settings.APP_NAME}")
        st.caption("Gestão de compras e controle de entregas com IA")

        if not settings.supabase_configurado:
            st.warning("⚠️ Supabase não configurado. Veja o .env / Secrets.")

        st.divider()

        escolha = st.radio(
            "Navegação",
            options=list(PAGINAS.keys()),
            format_func=lambda p: f"{PAGINAS[p]}  {p}",
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("v0.2.0 — em desenvolvimento")

    return escolha


# ---------------------------------------------------------------------------
# Roteamento
# ---------------------------------------------------------------------------
ROTAS = {
    "Dashboard": dashboard.render,
    "Cadastro": cadastro.render,
    "Timeline": timeline.render,
    "Histórico": historico.render,
    "Chat IA": chat_ia.render,
    "Fornecedores": fornecedores.render,
}


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------
def main():
    pagina_escolhida = render_sidebar()
    st.session_state.pagina_atual = pagina_escolhida

    render_pagina = ROTAS[pagina_escolhida]
    render_pagina()


if __name__ == "__main__":
    main()
