from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações do Deep Agent carregadas via .env e variáveis de ambiente."""

    # Provider: "anthropic" ou "openai"
    llm_provider: str = "anthropic"

    # Anthropic
    anthropic_api_key: str = ""
    model_name: str = "claude-sonnet-4-5-20250514"

    # OpenAI
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o"

    # Parametros compartilhados
    max_tokens: int = 4096
    temperature: float = 0.3

    # Google Sheets (Service Account JSON como string)
    google_credentials_json: str = ""
    google_auth_method: str = "service_account"  # "service_account" ou "oauth2"
    google_authorized_user_json: str = ""  # JSON do OAuth2 authorized_user (alternativa ao Service Account)

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # BigQuery
    gcp_project_id: str = ""

    # Autenticacao
    auth_secret_key: str = ""  # JWT secret (32+ chars) — obrigatorio em producao
    auth_cookie_key: str = ""  # Cookie secret para streamlit-authenticator (32+ chars)
    auth_config_yaml: str = ""  # YAML com credenciais de usuarios (bcrypt hash)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()


def get_llm():
    """Factory que retorna o LLM configurado (Claude ou GPT)."""
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model_name,
            api_key=settings.openai_api_key,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            timeout=60,
        )

    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=settings.model_name,
        api_key=settings.anthropic_api_key,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        timeout=60,
    )
