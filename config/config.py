from pathlib import Path

import toml
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.toml"


with open(CONFIG_FILE, "r") as f:
    config = toml.load(f)


class Settings(BaseSettings):
    # настройки из env
    openai_api_key: str
    host: str
    port: int
    reload: bool

    # настройки из config.toml
    app_name: str = config["app"]["name"]
    app_version: str = config["app"]["version"]

    console_log_level: str = config["logging"]["console_log_level"]
    file_log_level: str = config["logging"]["file_log_level"]

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_DIR}/.env", env_file_encoding="utf-8", case_sensitive=False
    )


settings = Settings()
