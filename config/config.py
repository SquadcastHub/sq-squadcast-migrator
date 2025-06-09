import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    system: str = os.getenv("SYSTEM", "opsgenie")

    pagerduty_api_token: str = os.getenv("PAGERDUTY_API_TOKEN", "")
    pagerduty_api_url: str = os.getenv("PAGERDUTY_API_URL", "https://api.pagerduty.com")

    opsgenie_api_key: str = os.getenv("OPSGENIE_API_KEY", "")
    opsgenie_api_url: str = os.getenv("OPSGENIE_API_URL", "https://api.opsgenie.com/v2")

    squadcast_refresh_token: str = os.getenv("SQUADCAST_REFRESH_TOKEN", "")
    squadcast_region: str = os.getenv("SQUADCAST_REGION", "us")

    dry_run: bool = os.getenv("DRY_RUN", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
