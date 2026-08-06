"""
Regras de negócio de compras (ordens de compra, cada uma com 1+ itens).

Regra de arquitetura: toda validação e decisão de negócio vive aqui.
components/ e pages/ chamam estas funções — nunca acessam database/ direto.
"""

from datetime import date
from typing import Any, Optional

from config.constants import DIAS_ALERTA_ATRASO, MAX_ITENS_POR_COMPRA, StatusCompra
from database import compras_repository as repo
from services import notificacoes_service


class ErroValidacao(Exception):
    """Levantado quando os dados de uma ordem de compra são inválidos."""


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


def _validar_itens(itens: list[dict[str, Any]]) -> None:
    if not itens:
        raise ErroValidacao("A ordem de compra precisa ter pelo menos 1 item.")

    for item in itens:
        descricao = item.get("descricao", "")
        quantidade = item.get("quantidade", 0)

        if not descricao or not str(descricao).strip():
            raise ErroValidacao("Todo item precisa ter uma descrição.")

        if quantidade < 1:
            raise ErroValidacao(f"A quantidade de '{descricao}' precisa ser pelo menos 1.")

        if quantidade > MAX_ITENS_POR_COMPRA:
            raise ErroValidacao(
                f"Quantidade máxima por item é {MAX_ITENS_POR_COMPRA} unidades "
                f"(item: '{descricao}')."
            )


def quantidade_total(compra: dict[str, Any]) -> int:
    """Soma as quantidades de todos os itens de uma ordem de compra."""
    itens = compra.get("compra_itens") or []
    return sum(item["quantidade"] for item in itens)


def criar_compra(
    titulo: str,
    itens: list[dict[str, Any]],
    fornecedor_id: Optional[str] = None,
    prazo_entrega: Optional[str] = None,
    criado_por: Optional[str] = None,
) -> dict[str, Any]:
    """
    Cria uma nova ordem de compra com 1 ou mais itens, status inicial
    'pendente', e já registra a primeira entrada na timeline.
    """
    if not titulo or not titulo.strip():
        raise ErroValidacao("A ordem de compra precisa de um título.")

    _validar_itens(itens)

    dados_ordem = {
        "titulo": titulo.strip(),
        "fornecedor_id": fornecedor_id,
        "prazo_entrega": prazo_entrega,
        "criado_por": criado_por,
        "status": StatusCompra.PENDENTE.value,
    }

    ordem = repo.criar(dados_ordem)
    itens_criados = repo.criar_itens(
        ordem["id"],
        [
            {"descricao": str(item["descricao"]).strip(), "quantidade": int(item["quantidade"])}
            for item in itens
        ],
    )
    ordem["compra_itens"] = itens_criados

    repo.registrar_historico(
        compra_id=ordem["id"],
        status_novo=StatusCompra.PENDENTE.value,
        observacao=f"Ordem criada com {len(itens_criados)} item(ns).",
    )
    return ordem


def listar_compras(status: Optional[StatusCompra] = None) -> list[dict[str, Any]]:
    """Lista ordens de compra (com itens embutidos), opcionalmente filtradas por status."""
    return repo.listar(status=status.value if status else None)


def obter_timeline(compra_id: str) -> list[dict[str, Any]]:
    """Retorna o histórico de status (timeline) de uma ordem de compra."""
    return repo.listar_historico(compra_id)


def mudar_status(
    compra_id: str,
    novo_status: StatusCompra,
    observacao: Optional[str] = None,
) -> dict[str, Any]:
    """
    Muda o status de uma ordem de compra, validando se a transição é
    permitida, e registra o evento na timeline. Dispara notificação quando relevante.
    """
    compra = repo.buscar_por_id(compra_id)
    if compra is None:
        raise ErroValidacao(f"Ordem de compra {compra_id} não encontrada.")

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
        notificacoes_service.notificar_entrega_concluida(compra_id, compra["titulo"])

    return atualizada


def verificar_atrasos() -> list[dict[str, Any]]:
    """
    Verifica ordens com prazo de entrega vencido há mais de
    DIAS_ALERTA_ATRASO dias e dispara notificação de atraso para cada uma.
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
                descricao=compra["titulo"],
                dias_atraso=dias_atraso,
            )
            atrasadas.append(compra)

    return atrasadas
