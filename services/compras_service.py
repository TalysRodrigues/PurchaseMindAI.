"""
Regras de negócio de compras.

Regra de arquitetura: toda validação e decisão de negócio vive aqui.
components/ e pages/ chamam estas funções — nunca acessam database/ direto.
"""

from datetime import date
from typing import Any, Optional

from config.constants import DIAS_ALERTA_ATRASO, MAX_ITENS_POR_COMPRA, StatusCompra
from database import compras_repository as repo
from services import notificacoes_service


class ErroValidacao(Exception):
    """Levantado quando os dados de uma compra são inválidos."""


class TransicaoInvalidaError(Exception):
    """Levantado ao tentar mudar o status de uma compra para um estado não permitido."""


# Mapa de transições permitidas: de qual status pra quais outros pode ir.
TRANSICOES_VALIDAS: dict[StatusCompra, set[StatusCompra]] = {
    StatusCompra.PENDENTE: {StatusCompra.APROVADA, StatusCompra.CANCELADA},
    StatusCompra.APROVADA: {StatusCompra.EM_TRANSITO, StatusCompra.CANCELADA},
    StatusCompra.EM_TRANSITO: {StatusCompra.ENTREGUE, StatusCompra.CANCELADA},
    StatusCompra.ENTREGUE: set(),  # status final
    StatusCompra.CANCELADA: set(),  # status final
}


def _validar_dados_compra(descricao: str, quantidade: int) -> None:
    if not descricao or not descricao.strip():
        raise ErroValidacao("A descrição da compra não pode estar vazia.")

    if quantidade < 1:
        raise ErroValidacao("A quantidade precisa ser pelo menos 1.")

    if quantidade > MAX_ITENS_POR_COMPRA:
        raise ErroValidacao(
            f"Quantidade máxima por compra é {MAX_ITENS_POR_COMPRA} itens."
        )


def criar_compra(
    descricao: str,
    quantidade: int = 1,
    fornecedor_id: Optional[str] = None,
    prazo_entrega: Optional[str] = None,
    criado_por: Optional[str] = None,
) -> dict[str, Any]:
    """
    Cria uma nova compra com status inicial 'pendente' e já registra
    a primeira entrada na timeline (histórico).
    """
    _validar_dados_compra(descricao, quantidade)

    dados = {
        "descricao": descricao.strip(),
        "quantidade": quantidade,
        "fornecedor_id": fornecedor_id,
        "prazo_entrega": prazo_entrega,
        "criado_por": criado_por,
        "status": StatusCompra.PENDENTE.value,
    }

    compra = repo.criar(dados)
    repo.registrar_historico(
        compra_id=compra["id"],
        status_novo=StatusCompra.PENDENTE.value,
        observacao="Compra criada.",
    )
    return compra


def listar_compras(status: Optional[StatusCompra] = None) -> list[dict[str, Any]]:
    """Lista compras, opcionalmente filtradas por status."""
    return repo.listar(status=status.value if status else None)


def obter_timeline(compra_id: str) -> list[dict[str, Any]]:
    """Retorna o histórico de status (timeline) de uma compra."""
    return repo.listar_historico(compra_id)


def mudar_status(
    compra_id: str,
    novo_status: StatusCompra,
    observacao: Optional[str] = None,
) -> dict[str, Any]:
    """
    Muda o status de uma compra, validando se a transição é permitida,
    e registra o evento na timeline. Dispara notificação quando relevante.
    """
    compra = repo.buscar_por_id(compra_id)
    if compra is None:
        raise ErroValidacao(f"Compra {compra_id} não encontrada.")

    status_atual = StatusCompra(compra["status"])
    permitidos = TRANSICOES_VALIDAS[status_atual]

    if novo_status not in permitidos:
        raise TransicaoInvalidaError(
            f"Não é possível mudar de '{status_atual.label}' para "
            f"'{novo_status.label}'. Transições permitidas: "
            f"{', '.join(s.label for s in permitidos) or 'nenhuma (status final)'}."
        )

    atualizada = repo.atualizar_status(compra_id, novo_status.value)
    repo.registrar_historico(
        compra_id=compra_id,
        status_novo=novo_status.value,
        status_anterior=status_atual.value,
        observacao=observacao,
    )

    if novo_status == StatusCompra.ENTREGUE:
        notificacoes_service.notificar_entrega_concluida(compra_id, compra["descricao"])

    return atualizada


def verificar_atrasos() -> list[dict[str, Any]]:
    """
    Verifica compras com prazo de entrega vencido há mais de
    DIAS_ALERTA_ATRASO dias e dispara notificação de atraso para cada uma.

    Pensado para ser chamado periodicamente (ex: toda vez que o Dashboard
    carrega, ou por um job agendado no futuro).
    """
    compras_em_andamento = [
        c
        for c in repo.listar()
        if c["status"] in (StatusCompra.APROVADA.value, StatusCompra.EM_TRANSITO.value)
    ]

    atrasadas = []
    hoje = date.today()

    for compra in compras_em_andamento:
        prazo = compra.get("prazo_entrega")
        if not prazo:
            continue

        prazo_data = date.fromisoformat(prazo)
        dias_atraso = (hoje - prazo_data).days

        if dias_atraso >= DIAS_ALERTA_ATRASO:
            notificacoes_service.notificar_atraso(
                compra_id=compra["id"],
                descricao=compra["descricao"],
                dias_atraso=dias_atraso,
            )
            atrasadas.append(compra)

    return atrasadas
