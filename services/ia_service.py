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


class IASemCreditosError(Exception):
    """Levantado especificamente quando a conta da Anthropic está sem créditos."""


@lru_cache(maxsize=1)
def _get_client() -> anthropic.Anthropic:
    """Cliente único (singleton) da Anthropic, reaproveitado entre chamadas."""
    if not settings.ANTHROPIC_API_KEY:
        raise IAServiceNaoImplementadoError(
            "ANTHROPIC_API_KEY não configurada. Adicione a chave no .env "
            "(local) ou nos Secrets (Streamlit Cloud) para habilitar a IA."
        )
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _chamar_ia(**kwargs: Any) -> Any:
    """Encapsula a chamada à API, traduzindo erros técnicos em exceções amigáveis."""
    client = _get_client()
    try:
        return client.messages.create(**kwargs)
    except anthropic.APIError as erro:
        mensagem = str(erro)
        if "credit balance" in mensagem.lower() or "credit_balance" in mensagem.lower():
            raise IASemCreditosError(
                "A conta da Anthropic está sem créditos. Acesse "
                "console.anthropic.com → Plans & Billing para adicionar "
                "créditos e voltar a usar a IA."
            ) from erro
        raise IAErroExecucaoError(f"Erro ao chamar a IA: {erro}") from erro


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
    """Monta um resumo em texto das ordens de compra atuais, para dar contexto ao chat."""
    if not compras:
        return "Nenhuma ordem de compra cadastrada ainda."

    linhas = []
    for c in compras[:30]:  # limita o contexto enviado à IA
        prazo = c.get("prazo_entrega") or "sem prazo"
        itens = c.get("compra_itens") or []
        resumo_itens = "; ".join(f"{i['descricao']} (x{i['quantidade']})" for i in itens)
        linhas.append(f"- {c['titulo']} | status: {c['status']} | prazo: {prazo} | itens: {resumo_itens}")
    return "\n".join(linhas)


def interpretar_cadastro(texto: str) -> dict[str, Any]:
    """
    Recebe um texto em linguagem natural (pode descrever 1 ou vários itens,
    ex: "comprar 10 cadeiras e 5 mesas até dia 20/08") e retorna um dict
    pronto para services.compras_service.criar_compra:
        {"titulo": ..., "itens": [{"descricao": ..., "quantidade": ...}, ...],
         "prazo_entrega": ...}
    """
    hoje = date.today().isoformat()

    system = (
        "Você extrai dados estruturados de ordens de compra descritas em "
        "linguagem natural, em português do Brasil. O texto pode descrever "
        "um ou vários itens diferentes na mesma ordem. "
        f"A data de hoje é {hoje}. "
        "Responda APENAS com um JSON válido, sem nenhum texto antes ou depois, "
        'no formato exato: {"titulo": "um título curto resumindo a ordem", '
        '"itens": [{"descricao": "nome do item", "quantidade": inteiro}, ...], '
        '"prazo_entrega": "YYYY-MM-DD" ou null se não houver prazo mencionado}'
    )

    resposta = _chamar_ia(
        model=MODEL,
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": texto}],
    )

    dados = _parsear_json(_extrair_texto(resposta))

    itens = dados.get("itens") or []
    if not itens:
        raise IAErroExecucaoError(
            "A IA não conseguiu identificar nenhum item de compra nesse texto."
        )

    return {
        "titulo": str(dados.get("titulo") or itens[0].get("descricao", "Nova compra")),
        "itens": [
            {"descricao": str(i["descricao"]), "quantidade": int(i.get("quantidade") or 1)}
            for i in itens
        ],
        "prazo_entrega": dados.get("prazo_entrega"),
    }


def responder_chat(mensagem: str, contexto: Optional[list[dict[str, Any]]] = None) -> str:
    """
    Recebe a mensagem do usuário (e o histórico da conversa) e retorna a
    resposta da IA, já com o contexto do estado atual das ordens de compra.
    """
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

    resposta = _chamar_ia(
        model=MODEL,
        max_tokens=500,
        system=system,
        messages=mensagens_api,
    )

    return _extrair_texto(resposta)
