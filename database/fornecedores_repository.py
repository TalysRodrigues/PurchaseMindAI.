"""
Acesso à tabela `fornecedores` no Supabase.

Regra de arquitetura: apenas leitura/escrita crua no banco.
"""

from typing import Any, Optional

from database.client import get_client

TABELA = "fornecedores"


def listar() -> list[dict[str, Any]]:
    """Lista todos os fornecedores cadastrados."""
    resposta = get_client().table(TABELA).select("*").order("nome").execute()
    return resposta.data


def buscar_por_id(fornecedor_id: str) -> Optional[dict[str, Any]]:
    """Busca um fornecedor pelo id. Retorna None se não existir."""
    resposta = (
        get_client()
        .table(TABELA)
        .select("*")
        .eq("id", fornecedor_id)
        .maybe_single()
        .execute()
    )
    return resposta.data if resposta else None


def criar(dados: dict[str, Any]) -> dict[str, Any]:
    """Insere um novo fornecedor."""
    resposta = get_client().table(TABELA).insert(dados).execute()
    return resposta.data[0]


def atualizar(fornecedor_id: str, dados: dict[str, Any]) -> dict[str, Any]:
    """Atualiza os dados de um fornecedor existente."""
    resposta = (
        get_client().table(TABELA).update(dados).eq("id", fornecedor_id).execute()
    )
    return resposta.data[0]


def excluir(fornecedor_id: str) -> None:
    """Remove um fornecedor pelo id."""
    get_client().table(TABELA).delete().eq("id", fornecedor_id).execute()
