"""
Regras de negócio de fornecedores.

Regra de arquitetura: validação e decisões de negócio aqui.
components/ e pages/ nunca acessam database/ direto.
"""

import re
from typing import Any, Optional

from database import fornecedores_repository as repo

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ErroValidacao(Exception):
    """Levantado quando os dados de um fornecedor são inválidos."""


def _validar_dados_fornecedor(nome: str, email: Optional[str]) -> None:
    if not nome or not nome.strip():
        raise ErroValidacao("O nome do fornecedor não pode estar vazio.")

    if email and not _EMAIL_REGEX.match(email):
        raise ErroValidacao(f"E-mail inválido: '{email}'.")


def cadastrar_fornecedor(
    nome: str,
    contato: Optional[str] = None,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    observacoes: Optional[str] = None,
) -> dict[str, Any]:
    """Cadastra um novo fornecedor, validando nome e e-mail."""
    _validar_dados_fornecedor(nome, email)

    dados = {
        "nome": nome.strip(),
        "contato": contato,
        "email": email,
        "telefone": telefone,
        "observacoes": observacoes,
    }
    return repo.criar(dados)


def listar_fornecedores() -> list[dict[str, Any]]:
    """Lista todos os fornecedores cadastrados."""
    return repo.listar()


def buscar_fornecedor(fornecedor_id: str) -> Optional[dict[str, Any]]:
    """Busca um fornecedor pelo id."""
    return repo.buscar_por_id(fornecedor_id)


def atualizar_fornecedor(fornecedor_id: str, dados: dict[str, Any]) -> dict[str, Any]:
    """Atualiza os dados de um fornecedor, validando o que for informado."""
    nome = dados.get("nome")
    email = dados.get("email")

    if nome is not None or email is not None:
        fornecedor_atual = repo.buscar_por_id(fornecedor_id)
        if fornecedor_atual is None:
            raise ErroValidacao(f"Fornecedor {fornecedor_id} não encontrado.")

        nome_final = nome if nome is not None else fornecedor_atual["nome"]
        email_final = email if email is not None else fornecedor_atual.get("email")
        _validar_dados_fornecedor(nome_final, email_final)

    return repo.atualizar(fornecedor_id, dados)


def remover_fornecedor(fornecedor_id: str) -> None:
    """Remove um fornecedor."""
    repo.excluir(fornecedor_id)
