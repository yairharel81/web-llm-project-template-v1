from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    secret_key: str = "change-me"
    frontend_url: str = "http://localhost:5173"

    # Database
    database_url: str = "postgresql+asyncpg://appuser:apppassword@localhost:5432/appdb"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    use_mock_gemini: bool = True

    # Brevo Email
    brevo_api_key: str = ""
    email_from: str = "noreply@yourdomain.com"
    email_from_name: str = "Your App"
    use_mock_email: bool = True

    # Google Cloud Storage
    gcs_bucket_name: str = ""
    gcs_project_id: str = ""
    use_mock_storage: bool = True

    # Firestore
    firestore_project_id: str = ""
    firestore_database: str = "(default)"
    use_mock_firestore: bool = True

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


settings = Settings()
