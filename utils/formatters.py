"""
Funções utilitárias genéricas — sem regra de negócio, sem UI, sem banco.
Podem ser usadas por qualquer camada (services/, components/, pages/).
"""

import re
from datetime import date, datetime
from typing import Optional

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def formatar_data_br(data_iso: Optional[str]) -> str:
    """Converte 'YYYY-MM-DD' para 'DD/MM/YYYY'. Retorna aviso se vazio."""
    if not data_iso:
        return "sem prazo definido"
    ano, mes, dia = data_iso.split("-")
    return f"{dia}/{mes}/{ano}"


def formatar_data_hora_br(data_iso: Optional[str]) -> str:
    """Converte um timestamp ISO (ex: vindo do Supabase) para 'DD/MM/YYYY HH:MM'."""
    if not data_iso:
        return "—"
    dt = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y %H:%M")


def email_valido(email: str) -> bool:
    """Valida um formato básico de e-mail (não substitui confirmação real por link)."""
    return bool(_EMAIL_REGEX.match(email))


def dias_entre(data_inicio: date, data_fim: date) -> int:
    """Retorna a diferença em dias inteiros entre duas datas."""
    return (data_fim - data_inicio).days


def truncar_texto(texto: str, tamanho: int = 60) -> str:
    """Corta um texto longo e adiciona '...' no final, útil para listas e tabelas."""
    texto = texto.strip()
    if len(texto) <= tamanho:
        return texto
    return texto[: tamanho - 1].rstrip() + "…"
