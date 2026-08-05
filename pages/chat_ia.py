"""
Página: Chat IA.
"""

import streamlit as st

from services import ia_service


def render() -> None:
    st.header("💬 Chat IA")

    if "chat_historico" not in st.session_state:
        st.session_state.chat_historico = []

    for mensagem in st.session_state.chat_historico:
        with st.chat_message(mensagem["role"]):
            st.write(mensagem["content"])

    pergunta = st.chat_input("Pergunte algo sobre suas compras...")

    if pergunta:
        st.session_state.chat_historico.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.write(pergunta)

        with st.chat_message("assistant"):
            try:
                resposta = ia_service.responder_chat(
                    pergunta, contexto=st.session_state.chat_historico
                )
                st.write(resposta)
                st.session_state.chat_historico.append(
                    {"role": "assistant", "content": resposta}
                )
            except ia_service.IAServiceNaoImplementadoError:
                aviso = (
                    "🚧 O Chat IA ainda não está configurado. "
                    "Assim que a chave da IA for adicionada, respondo por aqui."
                )
                st.info(aviso)
            except ia_service.IAErroExecucaoError as erro:
                st.error(f"Não consegui responder agora: {erro}")
