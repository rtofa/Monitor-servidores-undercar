from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    grafana_url_login: str
    grafana_url_dashboard: str
    grafana_url_api: str
    grafana_url_query: str
    grafana_user: str
    grafana_password: str

    # Variáveis do Chatbee (WhatsApp Oficial via Meta)
    chatbee_api_url: str
    chatbee_api_token: str
    chatbee_user_id: str
    chatbee_department_id: str
    chatbee_channel_id: str

    database_url: str

    admin_name: str
    admin_email: str
    admin_password: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()