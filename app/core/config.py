from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    grafana_url_login: str
    grafana_url_dashboard: str
    grafana_url_api: str
    grafana_user: str
    grafana_password: str

    # Novas variáveis do Chatwoot
    chatwoot_api_url: str
    chatwoot_token: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()