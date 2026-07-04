"""
File: config.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Central application configuration. Reads environment variables (provided by Docker Compose) and exposes them as a typed settings object that the rest of the backend imports. Keeping configuration in one place avoids scattering os.getenv calls across modules.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed view over the environment configuration."""

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/brewing_digital_twin"
    mongodb_db_name: str = "brewing_digital_twin"

    # MQTT broker (the real-SPS data path: publisher -> broker -> backend)
    mqtt_broker_host: str = "mosquitto"
    mqtt_broker_port: int = 1883
    mqtt_topic: str = "brauanlage/sps/live"

    # OPC-UA / SPS endpoint (now consumed by the mqtt_publisher, kept here for
    # reference / documentation of the real SPS address).
    opcua_server_url: str = "opc.tcp://192.168.0.10:4840"

    # Feature flags / runtime tuning
    enable_simulation_mode: bool = True
    collector_interval_seconds: float = 1.0
    sps_message_timeout_seconds: float = 10.0

    # Shared process simulator (backend simulation mode)
    simulation_total_duration_seconds: float = 1800.0
    simulation_tick_seconds: float = 1.0
    simulation_speed_factor: float = 1.0
    simulation_scenario: str = "NORMAL_PROCESS"

    # API
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Split the comma-separated CORS origins into a list for FastAPI."""
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance (read once per process)."""
    return Settings()


settings = get_settings()
