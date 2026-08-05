"""Pacote de configurações da aplicação PurchaseMind AI."""

from config.settings import settings
from config.constants import (
    StatusCompra,
    TipoNotificacao,
    PapelUsuario,
    MAX_ITENS_POR_COMPRA,
    DIAS_ALERTA_ATRASO,
)

__all__ = [
    "settings",
    "StatusCompra",
    "TipoNotificacao",
    "PapelUsuario",
    "MAX_ITENS_POR_COMPRA",
    "DIAS_ALERTA_ATRASO",
]
