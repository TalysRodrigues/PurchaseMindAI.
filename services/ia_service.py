"""
Serviço de IA: cadastro por linguagem natural e chat.

⚠️ AINDA NÃO IMPLEMENTADO — aguardando decisão do provedor (Claude ou OpenAI).

Regra de arquitetura: qualquer chamada de IA passa por aqui. components/ e
pages/ nunca chamam a API da IA diretamente — sempre por estas funções.
Isso significa que quando decidirmos o provedor, só este arquivo muda;
o resto do app não precisa saber qual IA está por trás.
"""

from typing import Any, Optional


class IAServiceNaoImplementadoError(NotImplementedError):
    """Levantado enquanto o provedor de IA não foi configurado."""


def interpretar_cadastro(texto: str) -> dict[str, Any]:
    """
    Recebe um texto em linguagem natural (ex: "comprar 10 cadeiras até dia 20/08")
    e deve retornar um dicionário pronto para services.compras_service.criar_compra:
        {"descricao": ..., "quantidade": ..., "prazo_entrega": ...}

    TODO: implementar chamada à API de IA (Claude ou GPT) assim que o
    provedor for escolhido.
    """
    raise IAServiceNaoImplementadoError(
        "Cadastro por linguagem natural ainda não está configurado. "
        "Defina o provedor de IA (Claude ou OpenAI) para habilitar esta função."
    )


def responder_chat(mensagem: str, contexto: Optional[list[dict[str, Any]]] = None) -> str:
    """
    Recebe uma mensagem do usuário (e opcionalmente o histórico da
    conversa) e retorna a resposta da IA sobre o estado das compras.

    TODO: implementar chamada à API de IA (Claude ou GPT) assim que o
    provedor for escolhido.
    """
    raise IAServiceNaoImplementadoError(
        "O Chat IA ainda não está configurado. "
        "Defina o provedor de IA (Claude ou OpenAI) para habilitar esta função."
    )
