from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    RABBIT_HOST: str
    RABBIT_PORT: str
    RABBIT_USER: str
    RABBIT_PASS: str

    API_KEY: str

    PUBLISH_LIMIT: int
    POLL_INTERVAL_SECONDS: int

    RETRY_HEADER: str
    LAST_ERROR_HEADER: str
    MAX_RETRY_COUNT: int
    BASE_RETRY_DELAY_SECONDS: int

    WEBHOOK_ATTEMPTS: int
    WEBHOOK_BASE_DELAY_SECONDS: int
    WEBHOOK_TIMEOUT_SECONDS: int

    PAYMENT_GATEWAY_SUCCESS_RATE: float
    PAYMENT_GATEWAY_MIN_DELAY_SECONDS: float
    PAYMENT_GATEWAY_MAX_DELAY_SECONDS: float

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASS}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"
