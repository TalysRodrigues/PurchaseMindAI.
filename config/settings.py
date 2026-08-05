"""
Configurações centrais da aplicação.

Regra de arquitetura: este módulo apenas LÊ configurações (variáveis de
ambiente, constantes globais). Nenhuma regra de negócio ou acesso a banco
deve entrar aqui.

Uso:
    from config.settings import settings

    print(settings.APP_NAME)
    print(settings.SUPABASE_URL)
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Carrega o arquivo .env (se existir) para variáveis de ambiente locais.
# Em produção (ex: Streamlit Cloud), as variáveis normalmente já vêm
# configuradas no ambiente, e o .env não é necessário.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Agrupa todas as configurações da aplicação em um único lugar."""

    # --- Aplicação ---
    APP_NAME: str = os.getenv("APP_NAME", "PurchaseMind AI")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_ICON: str = "🛒"

    # --- Supabase ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # --- IA ---
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def supabase_configurado(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)

    @property
    def ia_configurada(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY or self.OPENAI_API_KEY)


# Instância única, importada pelo resto da aplicação.
settings = Settings()
