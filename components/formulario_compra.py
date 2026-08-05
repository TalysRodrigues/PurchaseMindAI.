"""
Formulário de cadastro manual de uma nova compra.

Regra de arquitetura: coleta os dados na tela e repassa via callback
`on_submit`. Quem valida e salva de verdade é services/compras_service —
este componente não chama database/ nem services/ diretamente.
"""

from typing import Any, Callable, Optional

import streamlit as st

from config.constants import MAX_ITENS_POR_COMPRA


def render_formulario_nova_compra(
    fornecedores: list[dict[str, Any]],
    on_submit: Callable[[dict[str, Any]], None],
) -> None:
    """
    Desenha o formulário de nova compra. Ao enviar, chama
    `on_submit(dados)` com um dict pronto para
    services.compras_service.criar_compra(**dados).

    `fornecedores` é a lista de fornecedores já carregada (para o
    seletor) — este componente não busca isso sozinho.
    """
    opcoes_fornecedor: dict[str, Optional[str]] = {"Nenhum": None}
    opcoes_fornecedor.update({f["nome"]: f["id"] for f in fornecedores})

    with st.form("form_nova_compra", clear_on_submit=True):
        descricao = st.text_input("Descrição da compra*")
        quantidade = st.number_input(
            "Quantidade", min_value=1, max_value=MAX_ITENS_POR_COMPRA, value=1
        )
        fornecedor_nome = st.selectbox("Fornecedor", options=list(opcoes_fornecedor.keys()))
        prazo_entrega = st.date_input("Prazo de entrega", value=None)

        enviado = st.form_submit_button("Cadastrar compra", type="primary")

        if enviado:
            if not descricao.strip():
                st.error("A descrição da compra é obrigatória.")
                return

            dados = {
                "descricao": descricao,
                "quantidade": int(quantidade),
                "fornecedor_id": opcoes_fornecedor[fornecedor_nome],
                "prazo_entrega": prazo_entrega.isoformat() if prazo_entrega else None,
            }
            on_submit(dados)
