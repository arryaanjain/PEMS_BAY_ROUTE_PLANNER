"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Maps API
    google_maps_api_key: str
    
    # Database settings
    database_url: str | None = None
    db_user: str = "user"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: str = "3306"
    db_name: str = "sampledb"
    
    # PEMS Bay Region boundaries (approximate San Francisco Bay Area)
    pems_bay_center_lat: float = 37.7749
    pems_bay_center_lng: float = -122.4194
    pems_bay_radius_km: float = 50.0  # 50km radius
    
    # PEMS Bay bounding box (for strict validation)
    pems_bay_min_lat: float = 37.2
    pems_bay_max_lat: float = 38.3
    pems_bay_min_lng: float = -122.8
    pems_bay_max_lng: float = -121.8
    
    # API settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    def get_database_url(self) -> str:
        """Get database URL, constructing it from parts if not provided directly."""
        if self.database_url:
            return self.database_url
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# Global settings instance
settings = Settings()
