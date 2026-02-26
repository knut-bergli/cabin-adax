from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

import logging
import logging.config
import os

import yaml
from pathlib import Path


def get_project_root() -> Path:
    """
    Returns the project root directory by looking for markers like 'config_files' or 'pyproject.toml'.
    """
    here = Path(__file__).resolve().parent
    
    # Check current directory and parents for root markers
    for parent in [here] + list(here.parents):
        if (parent / 'config_files').exists() or (parent / 'pyproject.toml').exists():
            return parent
            
    # Fallback to the previous logic if no markers found
    if here.name == 'config' and here.parent.name == 'app':
        return here.parent.parent
    return here.parent.parent


def resolve_path(path: str | Path) -> Path:
    """
    Resolves a path relative to the project root and returns an absolute Path object.
    """
    p = Path(path)
    if p.is_absolute():
        if p.exists():
            return p.resolve()
        # If absolute path doesn't exist, maybe it was meant to be relative to root
        # (e.g. /config_files/logging.yaml when config_files is in project root)
        stripped_p = Path(str(path).lstrip('/'))
        root_p = get_project_root() / stripped_p
        if root_p.exists():
            return root_p.resolve()
        return p.absolute()

    # Try relative to CWD
    if p.exists():
        return p.resolve()

    # Try relative to project root
    root_p = get_project_root() / p
    return root_p.absolute()


class Settings(BaseSettings):
    """
    Class for keeping configurations.
    The configuration is loaded with python-dotenv package using load_dotenv()
    @lru_cache keeps the configuration in a local cache, so we don't need to load from file more than once
    """

    model_config = SettingsConfigDict(
        validate_default=False, 
        env_file=str(resolve_path('env_files/.env'))
    )
    AUTH_KEY: str
    AUTH_ALGORITHM: str
    AUTH_ACCESS_TIMEOUT: int
    AUTH_2FA_TIMEOUT: int
    DB_NAME: str
    LOGGER_NAME: str
    LOGGING_FILE_NAME: str
    ABOUT_IMAGE_FILE_NAME: str
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "Lax"
    DEV_MODE: bool = False
    TIMEZONE: str = "Europe/Oslo"


def _ensure_env_file():
    """
    Ensures that an .env file exists in the env_files directory.
    If it doesn't exist, it copies it from env_template.txt.
    """
    env_file = resolve_path('env_files/.env')
    if not env_file.exists():
        template_file = resolve_path('env_files/env_template.txt')
        if template_file.exists():
            import shutil
            env_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(template_file, env_file)
            logging.info(f"Created {env_file} from template.")
        else:
            logging.warning(f"Neither {env_file} nor {template_file} found.")


_ensure_env_file()
load_dotenv(resolve_path('env_files/.env'))


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_config_logging(default_path: str = '/config_files/logging.yaml', default_level: int = logging.INFO):
    """
    Load and configure logging settings for the application.

    Reads a YAML logging configuration and applies it via dictConfig. If the YAML
    cannot be read, falls back to a basic console logger.

    In addition, if a profile name is provided via the app Settings or environment
    (development/staging/production), the selected profile's level is applied to
    the root logger so all module loggers inherit it.
    """
    # Determine the profile to use (env overrides settings if provided later)
    try:
        profile = os.environ.get("LOGGER_NAME") or get_settings().LOGGER_NAME
    except Exception:
        # settings may not be initialized yet
        profile = os.environ.get("LOGGER_NAME", "development")

    resolved_path = resolve_path(default_path)

    if resolved_path.exists():
        try:
            with open(resolved_path, 'rt') as file:
                config = yaml.safe_load(file.read())

            # Ensure top-level root exists in YAML (older file versions may have root under loggers)
            if isinstance(config.get("loggers"), dict) and "root" in config.get("loggers", {}):
                # migrate to top-level root if needed
                root_cfg = config["loggers"].pop("root")
                config["root"] = root_cfg

            # Apply selected profile level to root
            prof_level = (
                config.get("loggers", {})
                .get(profile, {})
                .get("level")
            )
            if prof_level:
                config.setdefault("root", {})
                # Keep existing handlers if present
                if "handlers" not in config["root"]:
                    # reasonable safety default
                    config["root"]["handlers"] = ["console"]
                config["root"]["level"] = prof_level

            # Resolve paths for file handlers and ensure directories exist
            if "handlers" in config:
                for handler_name, handler_cfg in config["handlers"].items():
                    if "filename" in handler_cfg:
                        log_file = resolve_path(handler_cfg["filename"])
                        log_file.parent.mkdir(parents=True, exist_ok=True)
                        handler_cfg["filename"] = str(log_file)

            logging.config.dictConfig(config)
        except Exception as exc:  # catch any logging misconfig
            # Fallback to a basic, console-only logger to avoid crashing the app
            logging.basicConfig(level=default_level)
            logging.getLogger(__name__).warning(
                "Failed to initialize logging from %s (%s). Falling back to basic console logging.",
                resolved_path,
                exc,
            )
    else:
        logging.basicConfig(level=default_level)


def _load():
    # Determine logging YAML path
    logging_yaml = os.environ.get("LOGGING_FILE_NAME") or get_settings().LOGGING_FILE_NAME or os.path.join('config_files', 'logging.yaml')
    # Configure logging using the selected profile inside load_config_logging
    load_config_logging(logging_yaml)


# Runs automatically when the module is loaded
_load()
