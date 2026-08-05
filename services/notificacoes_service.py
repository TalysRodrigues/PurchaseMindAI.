"""
Regras de negócio de notificações.

Regra de arquitetura: aqui decidimos O QUÊ e QUANDO notificar.
database/notificacoes_repository.py só sabe gravar/ler no banco.
"""

from typing import Any

from config.constants import TipoNotificacao
from database import notificacoes_repository as repo


def notificar_nova_compra(compra_id: str, descricao: str) -> dict[str, Any]:
    """Notificação disparada quando uma nova compra é cadastrada."""
    return repo.criar(
        compra_id=compra_id,
        tipo=TipoNotificacao.NOVA_COMPRA.value,
        mensagem=f"Nova compra cadastrada: {descricao}",
    )


def notificar_mudanca_status(compra_id: str, descricao: str, novo_status_label: str) -> dict[str, Any]:
    """Notificação disparada quando o status de uma compra muda."""
    return repo.criar(
        compra_id=compra_id,
        tipo=TipoNotificacao.MUDANCA_STATUS.value,
        mensagem=f"'{descricao}' mudou para: {novo_status_label}",
    )


def notificar_atraso(compra_id: str, descricao: str, dias_atraso: int) -> dict[str, Any]:
    """Notificação disparada quando uma compra passa do prazo de entrega."""
    return repo.criar(
        compra_id=compra_id,
        tipo=TipoNotificacao.ATRASO_ENTREGA.value,
        mensagem=f"'{descricao}' está {dias_atraso} dia(s) atrasada.",
    )


def notificar_entrega_concluida(compra_id: str, descricao: str) -> dict[str, Any]:
    """Notificação disparada quando uma compra é marcada como entregue."""
    return repo.criar(
        compra_id=compra_id,
        tipo=TipoNotificacao.ENTREGA_CONCLUIDA.value,
        mensagem=f"'{descricao}' foi entregue.",
    )


def listar_pendentes() -> list[dict[str, Any]]:
    """Lista notificações ainda não lidas."""
    return repo.listar_nao_lidas()


def marcar_como_lida(notificacao_id: str) -> dict[str, Any]:
    """Marca uma notificação como lida."""
    return repo.marcar_como_lida(notificacao_id)
