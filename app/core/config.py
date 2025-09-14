"""
Configuration settings for the Insurance Claims Data Automation System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./insurance_claims.db"
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_default_region: str = "us-east-1"
    aws_s3_bucket: Optional[str] = None
    
    # Application
    app_name: str = "Insurance Claims Data Automation System"
    debug: bool = False
    log_level: str = "INFO"
    
    # Data Processing
    batch_size: int = 1000
    max_workers: int = 4
    
    # Reserve Calculation
    confidence_level: float = 0.95
    development_period: int = 12  # months
    tail_factor: float = 1.05
    
    # Dashboard
    dashboard_refresh_interval: int = 300  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()