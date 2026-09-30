from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

ACCESS_TOKEN_COOKIE_NAME = "access_token"


class Settings(BaseSettings):
    PASSWORD_HASH_SECRET: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION: int
    CLIENT_URL: str
    REDIS_TRANSPORTER: str
    REDIS_RESULTS: str

    # The users table has no role column yet. Every authenticated user resolves to
    # this role until RBAC lands; the field exists so the client contract does not
    # change when a real role column is added.
    DEFAULT_USER_ROLE: str = "user"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        """CLIENT_URL as a CORS-friendly list. Accepts comma-separated origins."""
        return [origin.strip() for origin in self.CLIENT_URL.split(",") if origin.strip()]

    @property
    def cookie_secure(self) -> bool:
        """Secure cookies require HTTPS, so only enable them for HTTPS client URLs.

        Browsers treat http://localhost and http://127.0.0.1 as trustworthy, but a
        Secure cookie set over plain http on any other host is silently dropped.
        """
        return self.CLIENT_URL.startswith("https://")

    @property
    def cookie_samesite(self) -> str:
        """SameSite=None requires Secure, which in turn requires HTTPS."""
        return "none" if self.cookie_secure else "lax"


@lru_cache
def get_settings():
    return Settings()


config = get_settings()
