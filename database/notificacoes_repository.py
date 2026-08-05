"""
Acesso à tabela `notificacoes` no Supabase.

Regra de arquitetura: apenas leitura/escrita crua no banco.
A decisão de QUANDO disparar uma notificação pertence a services/.
"""

from typing import Any

from database.client import get_client

TABELA = "notificacoes"


def listar_nao_lidas() -> list[dict[str, Any]]:
    """Lista notificações ainda não lidas, mais recentes primeiro."""
    resposta = (
        get_client()
        .table(TABELA)
        .select("*")
        .eq("lida", False)
        .order("criado_em", desc=True)
        .execute()
    )
    return resposta.data


def criar(compra_id: str, tipo: str, mensagem: str) -> dict[str, Any]:
    """Insere uma nova notificação."""
    resposta = (
        get_client()
        .table(TABELA)
        .insert({"compra_id": compra_id, "tipo": tipo, "mensagem": mensagem})
        .execute()
    )
    return resposta.data[0]


def marcar_como_lida(notificacao_id: str) -> dict[str, Any]:
    """Marca uma notificação como lida."""
    resposta = (
        get_client()
        .table(TABELA)
        .update({"lida": True})
        .eq("id", notificacao_id)
        .execute()
    )
    return resposta.data[0]
