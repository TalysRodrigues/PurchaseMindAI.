"""
Acesso à tabela `compras` (ordens de compra) e `compra_itens` no Supabase.

Regra de arquitetura: apenas leitura/escrita crua no banco.
Validações e regras de negócio pertencem a services/.
"""

from typing import Any, Optional

from database.client import get_client

TABELA = "compras"
TABELA_ITENS = "compra_itens"

# select usado em listar/buscar: traz os itens já embutidos numa única consulta
_SELECT_COM_ITENS = f"*, {TABELA_ITENS}(*)"


def listar(status: Optional[str] = None) -> list[dict[str, Any]]:
    """Lista ordens de compra (com seus itens embutidos), opcionalmente por status."""
    query = (
        get_client()
        .table(TABELA)
        .select(_SELECT_COM_ITENS)
        .order("criado_em", desc=True)
    )
    if status:
        query = query.eq("status", status)
    resposta = query.execute()
    return resposta.data


def buscar_por_id(compra_id: str) -> Optional[dict[str, Any]]:
    """Busca uma ordem de compra (com itens) pelo id. Retorna None se não existir."""
    resposta = (
        get_client()
        .table(TABELA)
        .select(_SELECT_COM_ITENS)
        .eq("id", compra_id)
        .maybe_single()
        .execute()
    )
    return resposta.data if resposta else None


def criar(dados: dict[str, Any]) -> dict[str, Any]:
    """Insere uma nova ordem de compra (sem os itens ainda). `dados` já validado por services/."""
    resposta = get_client().table(TABELA).insert(dados).execute()
    return resposta.data[0]


def criar_itens(compra_id: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Insere em lote os itens de uma ordem de compra."""
    linhas = [{**item, "compra_id": compra_id} for item in itens]
    resposta = get_client().table(TABELA_ITENS).insert(linhas).execute()
    return resposta.data


def atualizar_status(compra_id: str, novo_status: str) -> dict[str, Any]:
    """Atualiza apenas o status de uma ordem de compra."""
    resposta = (
        get_client()
        .table(TABELA)
        .update({"status": novo_status})
        .eq("id", compra_id)
        .execute()
    )
    return resposta.data[0]


def excluir(compra_id: str) -> None:
    """Remove uma ordem de compra pelo id (os itens saem junto, via cascade)."""
    get_client().table(TABELA).delete().eq("id", compra_id).execute()


def registrar_historico(
    compra_id: str,
    status_novo: str,
    status_anterior: Optional[str] = None,
    observacao: Optional[str] = None,
) -> dict[str, Any]:
    """Insere um registro na timeline (compras_historico) de uma ordem de compra."""
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
    """Lista a timeline de status de uma ordem de compra, mais antiga primeiro."""
    resposta = (
        get_client()
        .table("compras_historico")
        .select("*")
        .eq("compra_id", compra_id)
        .order("criado_em")
        .execute()
    )
    return resposta.data
