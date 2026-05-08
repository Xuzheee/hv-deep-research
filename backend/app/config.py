from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hv_analysis.db"
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_timeout_seconds: int = 60
    llm_temperature: float = 0.2
    run_real_tool_tests: bool = False
    run_real_llm_tests: bool = False
    external_tool_validation_timeout_seconds: int = 30
    reports_output_dir: str = "backend/app/outputs/reports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
