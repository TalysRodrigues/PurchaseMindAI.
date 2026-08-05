"""
Acesso à tabela `compras` no Supabase.

Regra de arquitetura: apenas leitura/escrita crua no banco.
Validações e regras de negócio (ex: "não pode ter mais de X itens")
pertencem a services/, não aqui.
"""

from typing import Any, Optional

from database.client import get_client

TABELA = "compras"


def listar(status: Optional[str] = None) -> list[dict[str, Any]]:
    """Lista compras, opcionalmente filtradas por status."""
    query = get_client().table(TABELA).select("*").order("criado_em", desc=True)
    if status:
        query = query.eq("status", status)
    resposta = query.execute()
    return resposta.data


def buscar_por_id(compra_id: str) -> Optional[dict[str, Any]]:
    """Busca uma compra específica pelo id. Retorna None se não existir."""
    resposta = (
        get_client()
        .table(TABELA)
        .select("*")
        .eq("id", compra_id)
        .maybe_single()
        .execute()
    )
    return resposta.data if resposta else None


def criar(dados: dict[str, Any]) -> dict[str, Any]:
    """Insere uma nova compra. `dados` já deve vir validado por services/."""
    resposta = get_client().table(TABELA).insert(dados).execute()
    return resposta.data[0]


def atualizar_status(compra_id: str, novo_status: str) -> dict[str, Any]:
    """Atualiza apenas o status de uma compra."""
    resposta = (
        get_client()
        .table(TABELA)
        .update({"status": novo_status})
        .eq("id", compra_id)
        .execute()
    )
    return resposta.data[0]


def excluir(compra_id: str) -> None:
    """Remove uma compra pelo id."""
    get_client().table(TABELA).delete().eq("id", compra_id).execute()


def registrar_historico(
    compra_id: str,
    status_novo: str,
    status_anterior: Optional[str] = None,
    observacao: Optional[str] = None,
) -> dict[str, Any]:
    """Insere um registro na timeline (compras_historico) de uma compra."""
    resposta = (
        get_client()
        .table("compras_historico")
        .insert(
            {
                "compra_id": compra_id,
                "status_anterior": status_anterior,
                "status_novo": status_novo,
                "observacao": observacao,
            }
        )
        .execute()
    )
    return resposta.data[0]


def listar_historico(compra_id: str) -> list[dict[str, Any]]:
    """Lista a timeline de status de uma compra, mais antiga primeiro."""
    resposta = (
        get_client()
        .table("compras_historico")
        .select("*")
        .eq("compra_id", compra_id)
        .order("criado_em")
        .execute()
    )
    return resposta.data
