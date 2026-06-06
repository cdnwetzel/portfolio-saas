from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://saas_user:saas_password@localhost:5432/saas_prod")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Stripe
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # GitHub
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")

    # Application
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    frontend_url: str = os.getenv("FRONTEND_URL", "https://app.yourdomain.com")

    # GPU Inference
    model_id: str = os.getenv("MODEL_ID", "meta-llama/Llama-2-70b-chat-hf")
    tensor_parallel_size: int = int(os.getenv("TENSOR_PARALLEL_SIZE", "2"))
    gpu_memory_utilization: float = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.85"))

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
