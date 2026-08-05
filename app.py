"""
PurchaseMind AI - Ponto de entrada da aplicação.

Regra de arquitetura: este arquivo APENAS inicializa o sistema
(configuração de página, estado de sessão e roteamento entre seções).
Nenhuma regra de negócio deve ser implementada aqui — isso pertence a services/.
Nenhum acesso a banco deve ser feito aqui — isso pertence a database/.

Enquanto config/, services/, database/, components/ e pages/ ainda não existem,
este arquivo roda de forma independente, com placeholders visuais para cada
seção. Conforme as pastas forem criadas, cada bloco "TODO" abaixo será
substituído pela chamada real ao módulo correspondente.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
# TODO: quando config/ existir, mover estes valores para config/settings.py
APP_NAME = "PurchaseMind AI"
APP_ICON = "🛒"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estado de sessão
# ---------------------------------------------------------------------------
# TODO: quando services/ existir, o estado inicial pode vir de lá
# (ex: usuário autenticado, contexto do chat IA, etc.)
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
        st.title(f"{APP_ICON} {APP_NAME}")
        st.caption("Gestão de compras e controle de entregas com IA")
        st.divider()

        escolha = st.radio(
            "Navegação",
            options=list(PAGINAS.keys()),
            format_func=lambda p: f"{PAGINAS[p]}  {p}",
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("v0.1.0 — em desenvolvimento")

    return escolha


# ---------------------------------------------------------------------------
# Páginas (placeholders até pages/ existir)
# ---------------------------------------------------------------------------
# TODO: mover cada função abaixo para pages/<nome>.py quando a pasta existir.
# TODO: cada página deve buscar dados via services/, nunca direto do banco.

def pagina_dashboard():
    st.header("📊 Dashboard")
    st.info("Em breve: indicadores de compras, gastos e entregas.")


def pagina_cadastro():
    st.header("📝 Cadastro por linguagem natural")
    st.info("Em breve: campo de texto livre interpretado pela IA para registrar uma nova compra.")
    st.text_area("Descreva a compra", placeholder="Ex: Comprar 10 cadeiras de escritório até dia 20/08")


def pagina_timeline():
    st.header("🕒 Timeline")
    st.info("Em breve: linha do tempo das compras em andamento.")


def pagina_historico():
    st.header("📚 Histórico")
    st.info("Em breve: histórico completo de compras e entregas.")


def pagina_chat_ia():
    st.header("💬 Chat IA")
    st.info("Em breve: assistente conversacional para consultas sobre compras.")
    st.chat_input("Pergunte algo sobre suas compras...")


def pagina_fornecedores():
    st.header("🚚 Controle de fornecedores")
    st.info("Em breve: cadastro e acompanhamento de fornecedores.")


ROTAS = {
    "Dashboard": pagina_dashboard,
    "Cadastro": pagina_cadastro,
    "Timeline": pagina_timeline,
    "Histórico": pagina_historico,
    "Chat IA": pagina_chat_ia,
    "Fornecedores": pagina_fornecedores,
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
