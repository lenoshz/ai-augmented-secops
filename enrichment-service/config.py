"""Application configuration for the GenesisSOC enrichment service."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed environment-backed settings for service configuration."""

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    elastic_password: str = Field(default="", alias="ELASTIC_PASSWORD")
    elasticsearch_url: str = Field(default="http://localhost:9200", alias="ELASTICSEARCH_URL")
    kibana_url: str = Field(default="http://localhost:5601", alias="KIBANA_URL")
    virustotal_api_key: str = Field(default="", alias="VIRUSTOTAL_API_KEY")
    abuseipdb_api_key: str = Field(default="", alias="ABUSEIPDB_API_KEY")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    enable_ioc_lookup: bool = Field(default=True, alias="ENABLE_IOC_LOOKUP")
    enable_asset_criticality: bool = Field(default=True, alias="ENABLE_ASSET_CRITICALITY")
    enable_feedback_loop: bool = Field(default=True, alias="ENABLE_FEEDBACK_LOOP")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
