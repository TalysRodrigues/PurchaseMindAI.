"""
Página: Cadastro de ordens de compra (manual, com múltiplos itens, e por
linguagem natural).
"""

import streamlit as st

from components.formulario_compra import render_formulario_nova_compra
from services import compras_service, fornecedores_service, ia_service
from services.compras_service import ErroValidacao


def render() -> None:
    st.header("📝 Cadastro de compras")

    aba_manual, aba_ia = st.tabs(["Cadastro manual", "Cadastro por linguagem natural"])

    # --- Aba: formulário manual (múltiplos itens) --------------------------
    with aba_manual:
        try:
            fornecedores = fornecedores_service.listar_fornecedores()
        except Exception as erro:
            st.warning(f"Não foi possível carregar fornecedores: {erro}")
            fornecedores = []

        def _ao_enviar(dados: dict) -> None:
            try:
                ordem = compras_service.criar_compra(**dados)
                qtd_itens = len(ordem.get("compra_itens", []))
                st.success(f"Ordem '{ordem['titulo']}' cadastrada com {qtd_itens} item(ns)!")
            except ErroValidacao as erro:
                st.error(str(erro))

        render_formulario_nova_compra(fornecedores, on_submit=_ao_enviar)

    # --- Aba: linguagem natural (IA) ----------------------------------------
    with aba_ia:
        st.caption(
            "Descreva a compra em texto livre — pode ter mais de um item. "
            "Ex: 'comprar 10 cadeiras e 5 mesas de escritório até dia 20/08'"
        )
        texto = st.text_area(
            "Descreva a compra",
            placeholder="Ex: Comprar 10 cadeiras e 5 mesas de escritório até dia 20/08",
        )

        if st.button("Interpretar e cadastrar", type="primary"):
            if not texto.strip():
                st.error("Descreva a compra antes de enviar.")
            else:
                try:
                    dados_interpretados = ia_service.interpretar_cadastro(texto)
                    ordem = compras_service.criar_compra(**dados_interpretados)
                    qtd_itens = len(ordem.get("compra_itens", []))
                    st.success(f"Ordem '{ordem['titulo']}' cadastrada via IA com {qtd_itens} item(ns)!")
                except ia_service.IAServiceNaoImplementadoError:
                    st.info(
                        "🚧 O cadastro por IA ainda não está ligado — "
                        "assim que o Chat IA for configurado, esta aba passa a funcionar."
                    )
                except ia_service.IASemCreditosError as erro:
                    st.error(str(erro))
                except ia_service.IAErroExecucaoError as erro:
                    st.error(f"A IA não conseguiu processar esse texto: {erro}")
                except ErroValidacao as erro:
                    st.error(str(erro))
