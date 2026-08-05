"""
Constantes globais da aplicação.

Regra de arquitetura: valores fixos usados em várias partes do sistema
(status, rótulos, tipos) ficam centralizados aqui — nunca espalhados
como strings soltas em services/, components/ ou pages/.
"""

from enum import Enum


class StatusCompra(str, Enum):
    """Status possíveis de uma compra, do cadastro até a entrega."""

    PENDENTE = "pendente"
    APROVADA = "aprovada"
    EM_TRANSITO = "em_transito"
    ENTREGUE = "entregue"
    CANCELADA = "cancelada"

    @property
    def label(self) -> str:
        """Texto amigável para exibir na interface."""
        return {
            StatusCompra.PENDENTE: "Pendente",
            StatusCompra.APROVADA: "Aprovada",
            StatusCompra.EM_TRANSITO: "Em trânsito",
            StatusCompra.ENTREGUE: "Entregue",
            StatusCompra.CANCELADA: "Cancelada",
        }[self]

    @property
    def icone(self) -> str:
        """Ícone para exibir junto do status na interface."""
        return {
            StatusCompra.PENDENTE: "⏳",
            StatusCompra.APROVADA: "✅",
            StatusCompra.EM_TRANSITO: "🚚",
            StatusCompra.ENTREGUE: "📦",
            StatusCompra.CANCELADA: "❌",
        }[self]


class TipoNotificacao(str, Enum):
    """Tipos de notificação que o sistema pode disparar."""

    NOVA_COMPRA = "nova_compra"
    MUDANCA_STATUS = "mudanca_status"
    ATRASO_ENTREGA = "atraso_entrega"
    ENTREGA_CONCLUIDA = "entrega_concluida"


class PapelUsuario(str, Enum):
    """Papéis de usuário no sistema (banco compartilhado)."""

    ADMIN = "admin"
    COMPRADOR = "comprador"
    VISUALIZADOR = "visualizador"


# Limites e valores padrão usados em vários pontos do sistema
MAX_ITENS_POR_COMPRA = 50
DIAS_ALERTA_ATRASO = 2  # dispara notificação de atraso após X dias do prazo
