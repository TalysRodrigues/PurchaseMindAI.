"""
Formulário de cadastro de uma nova ordem de compra, com um ou mais itens.

Regra de arquitetura: coleta os dados na tela e repassa via callback
`on_submit`. Quem valida e salva de verdade é services/compras_service —
este componente não chama database/ nem services/ diretamente.
"""

from typing import Any, Callable, Optional

import pandas as pd
import streamlit as st

from config.constants import MAX_ITENS_POR_COMPRA

_COLUNAS_ITENS = {"Descrição": "", "Quantidade": 1}


def render_formulario_nova_compra(
    fornecedores: list[dict[str, Any]],
    on_submit: Callable[[dict[str, Any]], None],
) -> None:
    """
    Desenha o formulário de nova ordem de compra, com uma tabela editável
    de itens (adicione/remova linhas livremente). Ao enviar, chama
    `on_submit(dados)` com um dict pronto para
    services.compras_service.criar_compra(**dados).

    `fornecedores` é a lista de fornecedores já carregada (para o
    seletor) — este componente não busca isso sozinho.
    """
    opcoes_fornecedor: dict[str, Optional[str]] = {"Nenhum": None}
    opcoes_fornecedor.update({f["nome"]: f["id"] for f in fornecedores})

    with st.form("form_nova_compra", clear_on_submit=True):
        titulo = st.text_input(
            "Título da ordem de compra*",
            placeholder="Ex: Reposição de material de escritório - Agosto",
        )
        fornecedor_nome = st.selectbox("Fornecedor", options=list(opcoes_fornecedor.keys()))
        prazo_entrega = st.date_input("Prazo de entrega", value=None, format="DD/MM/YYYY")

        st.caption("Itens da compra — clique no + para adicionar mais linhas")
        tabela_itens = st.data_editor(
            pd.DataFrame([_COLUNAS_ITENS]),
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="tabela_itens_nova_compra",
            column_config={
                "Descrição": st.column_config.TextColumn(required=True),
                "Quantidade": st.column_config.NumberColumn(
                    min_value=1, max_value=MAX_ITENS_POR_COMPRA, step=1, required=True
                ),
            },
        )

        enviado = st.form_submit_button("Cadastrar ordem de compra", type="primary")

        if enviado:
            if not titulo.strip():
                st.error("Informe um título para a ordem de compra.")
                return

            itens = [
                {"descricao": str(linha["Descrição"]).strip(), "quantidade": int(linha["Quantidade"])}
                for _, linha in tabela_itens.iterrows()
                if str(linha["Descrição"]).strip()
            ]

            if not itens:
                st.error("Adicione pelo menos 1 item com descrição preenchida.")
                return

            dados = {
                "titulo": titulo,
                "itens": itens,
                "fornecedor_id": opcoes_fornecedor[fornecedor_nome],
                "prazo_entrega": prazo_entrega.isoformat() if prazo_entrega else None,
            }
            on_submit(dados)
