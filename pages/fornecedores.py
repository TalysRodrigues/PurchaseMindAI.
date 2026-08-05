"""
Página: Controle de fornecedores.
"""

import streamlit as st

from services import fornecedores_service
from services.fornecedores_service import ErroValidacao


def render() -> None:
    st.header("🚚 Fornecedores")

    with st.expander("➕ Cadastrar novo fornecedor"):
        with st.form("form_fornecedor", clear_on_submit=True):
            nome = st.text_input("Nome*")
            contato = st.text_input("Pessoa de contato")
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone")
            observacoes = st.text_area("Observações")

            enviado = st.form_submit_button("Cadastrar", type="primary")

            if enviado:
                try:
                    fornecedores_service.cadastrar_fornecedor(
                        nome=nome,
                        contato=contato or None,
                        email=email or None,
                        telefone=telefone or None,
                        observacoes=observacoes or None,
                    )
                    st.success(f"Fornecedor '{nome}' cadastrado!")
                    st.rerun()
                except ErroValidacao as erro:
                    st.error(str(erro))

    st.divider()

    try:
        fornecedores = fornecedores_service.listar_fornecedores()
    except Exception as erro:
        st.error(f"Não foi possível carregar fornecedores: {erro}")
        return

    if not fornecedores:
        st.caption("Nenhum fornecedor cadastrado ainda.")
        return

    for fornecedor in fornecedores:
        with st.container(border=True):
            st.markdown(f"**{fornecedor['nome']}**")
            detalhes = []
            if fornecedor.get("contato"):
                detalhes.append(f"Contato: {fornecedor['contato']}")
            if fornecedor.get("email"):
                detalhes.append(f"E-mail: {fornecedor['email']}")
            if fornecedor.get("telefone"):
                detalhes.append(f"Telefone: {fornecedor['telefone']}")
            if detalhes:
                st.caption(" · ".join(detalhes))
