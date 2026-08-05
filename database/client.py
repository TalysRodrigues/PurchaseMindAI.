"""
Cliente de conexão com o Supabase.

Regra de arquitetura: acesso ao banco SOMENTE aqui em database/.
Nenhuma regra de negócio deve entrar neste módulo — isso pertence a services/.

Uso:
    from database.client import get_client

    supabase = get_client()
    supabase.table("compras").select("*").execute()
"""

from functools import lru_cache

from supabase import Client, create_client

from config.settings import settings


class SupabaseNaoConfiguradoError(Exception):
    """Levantado quando SUPABASE_URL / SUPABASE_KEY não estão definidos."""


@lru_cache(maxsize=1)
def get_client() -> Client:
    """
    Retorna uma instância única (singleton) do cliente Supabase.

    Usa lru_cache para reaproveitar a mesma conexão em toda a aplicação,
    evitando recriar o client a cada chamada.
    """
    if not settings.supabase_configurado:
        raise SupabaseNaoConfiguradoError(
            "SUPABASE_URL e SUPABASE_KEY precisam estar definidos no .env "
            "para conectar ao banco."
        )

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
