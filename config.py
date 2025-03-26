from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Загрузка конфига
    """
    TG_TOKEN: str
    MPSTAT_TOKEN: str
    GS_DOC_KEY: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
