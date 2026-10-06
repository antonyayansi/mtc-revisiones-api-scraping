from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    captcha_max_retries: int = 3
    openai_model: str = "gpt-4o-mini"
    mtc_base_url: str = "https://rec.mtc.gob.pe"
    request_timeout: float = 30.0


settings = Settings()
