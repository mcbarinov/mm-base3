from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServerConfig(BaseSettings):
    domain: str
    access_token: str
    use_https: bool = True
    tags: list[str]
    main_menu: dict[str, str]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
