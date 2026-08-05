"""
Serviço de IA: cadastro por linguagem natural e chat, usando a API da Anthropic (Claude).

Regra de arquitetura: qualquer chamada de IA passa por aqui. components/ e
pages/ nunca chamam a API da IA diretamente — sempre por estas funções.
"""

import json
from datetime import date
from functools import lru_cache
from typing import Any, Optional

import anthropic

from config.settings import settings

MODEL = "claude-sonnet-5"


class IAServiceNaoImplementadoError(Exception):
    """Levantado quando a chave de API da IA não está configurada."""


class IAErroExecucaoError(Exception):
    """Levantado quando a chamada à IA falha ou retorna algo inesperado."""


@lru_cache(maxsize=1)
def _get_client() -> anthropic.Anthropic:
    """Cliente único (singleton) da Anthropic, reaproveitado entre chamadas."""
    if not settings.ANTHROPIC_API_KEY:
        raise IAServiceNaoImplementadoError(
            "ANTHROPIC_API_KEY não configurada. Adicione a chave no .env "
            "(local) ou nos Secrets (Streamlit Cloud) para habilitar a IA."
        )
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _extrair_texto(resposta: Any) -> str:
    """Extrai o texto de uma resposta da API (pode vir em múltiplos blocos)."""
    partes = [bloco.text for bloco in resposta.content if bloco.type == "text"]
    return "\n".join(partes).strip()


def _parsear_json(texto: str) -> dict[str, Any]:
    """Faz parse do JSON retornado pela IA, tolerando blocos ```json ... ```."""
    limpo = texto.strip()
    if limpo.startswith("```"):
        linhas = limpo.split("\n")
        linhas = [l for l in linhas if not l.strip().startswith("```")]
        limpo = "\n".join(linhas).strip()

    try:
        return json.loads(limpo)
    except json.JSONDecodeError as erro:
        raise IAErroExecucaoError(
            f"A IA retornou um formato inesperado: {texto[:200]}"
        ) from erro


def _montar_resumo_compras(compras: list[dict[str, Any]]) -> str:
    """Monta um resumo em texto das compras atuais, para dar contexto ao chat."""
    if not compras:
        return "Nenhuma compra cadastrada ainda."

    linhas = []
    for c in compras[:30]:  # limita o contexto enviado à IA
        prazo = c.get("prazo_entrega") or "sem prazo"
        linhas.append(f"- {c['descricao']} | qtd: {c['quantidade']} | status: {c['status']} | prazo: {prazo}")
    return "\n".join(linhas)


def interpretar_cadastro(texto: str) -> dict[str, Any]:
    """
    Recebe um texto em linguagem natural (ex: "comprar 10 cadeiras até dia 20/08")
    e retorna um dict pronto para services.compras_service.criar_compra:
        {"descricao": ..., "quantidade": ..., "prazo_entrega": ...}
    """
    client = _get_client()
    hoje = date.today().isoformat()

    system = (
        "Você extrai dados estruturados de pedidos de compra descritos em "
        "linguagem natural, em português do Brasil. "
        f"A data de hoje é {hoje}. "
        "Responda APENAS com um JSON válido, sem nenhum texto antes ou depois, "
        'no formato exato: {"descricao": "string curta do item", '
        '"quantidade": inteiro (1 se não mencionado), '
        '"prazo_entrega": "YYYY-MM-DD" ou null se não houver prazo mencionado}'
    )

    try:
        resposta = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=system,
            messages=[{"role": "user", "content": texto}],
        )
    except anthropic.APIError as erro:
        raise IAErroExecucaoError(f"Erro ao chamar a IA: {erro}") from erro

    dados = _parsear_json(_extrair_texto(resposta))

    if not dados.get("descricao"):
        raise IAErroExecucaoError(
            "A IA não conseguiu identificar uma descrição de compra nesse texto."
        )

    return {
        "descricao": str(dados["descricao"]),
        "quantidade": int(dados.get("quantidade") or 1),
        "prazo_entrega": dados.get("prazo_entrega"),
    }


def responder_chat(mensagem: str, contexto: Optional[list[dict[str, Any]]] = None) -> str:
    """
    Recebe a mensagem do usuário (e o histórico da conversa) e retorna a
    resposta da IA, já com o contexto do estado atual das compras.
    """
    client = _get_client()

    # import local para evitar import circular na inicialização do pacote services/
    from services.compras_service import listar_compras

    resumo = _montar_resumo_compras(listar_compras())
    system = (
        "Você é o assistente de compras do PurchaseMind AI. Responda em "
        "português do Brasil, de forma direta e útil, com base nos dados "
        f"abaixo:\n\n{resumo}"
    )

    if contexto:
        mensagens_api = [
            {"role": m["role"], "content": m["content"]}
            for m in contexto
            if m.get("role") in ("user", "assistant")
        ]
    else:
        mensagens_api = [{"role": "user", "content": mensagem}]

    try:
        resposta = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=system,
            messages=mensagens_api,
        )
    except anthropic.APIError as erro:
        raise IAErroExecucaoError(f"Erro ao chamar a IA: {erro}") from erro

    return _extrair_texto(resposta)
