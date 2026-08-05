"""Pacote de acesso a dados da aplicação PurchaseMind AI (Supabase)."""

from database.client import get_client, SupabaseNaoConfiguradoError

__all__ = ["get_client", "SupabaseNaoConfiguradoError"]
