from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ANTHROPIC_API_KEY: str = ""
    BRIGHT_DATA_API_KEY: str = ""
    BRIGHT_DATA_SCRAPER_ZONE: str = ""
    BRIGHT_DATA_SERP_ZONE: str = ""
    BRIGHT_DATA_UNLOCKER_ZONE: str = ""
    BRIGHT_DATA_BROWSER_WS: str = ""
    BRIGHT_DATA_MCP_URL: str = "https://mcp.brightdata.com"
    FEATHERLESS_API_KEY: str = ""
    FEATHERLESS_BASE_URL: str = "https://api.featherless.ai/v1"
    COGNEE_API_KEY: str = ""
    COGNEE_BASE_URL: str = "https://api.cognee.ai"
    TRIGGERWARE_API_KEY: str = ""
    TRIGGERWARE_BASE_URL: str = "https://api.triggerware.ai/v1"
    TRIGGERWARE_WEBHOOK_SECRET: str = "secret"
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinel.db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change_me"
    CORS_ORIGINS: str = "http://localhost:3000"
    DEMO_MODE: bool = True  # Set False when real API keys are configured


settings = Settings()
