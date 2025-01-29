from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings for the application.

    Attributes:
        database_url (str): The database URL.
        bot_token (str): The Telegram bot token.
        secret_key (str): The secret key for authorization.
    """
    database_url: str
    bot_token: str
    # secret_key: str
    # gpt_key: str
    app_host: str
    app_port: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()