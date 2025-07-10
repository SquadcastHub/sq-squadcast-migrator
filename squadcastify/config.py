import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    source: str = os.getenv("SOURCE", "opsgenie")
    pagerduty_api_token: str = os.getenv("PAGERDUTY_API_TOKEN", "")
    pagerduty_api_url: str = os.getenv("PAGERDUTY_API_URL", "https://api.pagerduty.com")
    opsgenie_api_key: str = os.getenv("OPSGENIE_API_KEY", "")
    opsgenie_api_url: str = os.getenv("OPSGENIE_API_URL", "https://api.opsgenie.com/v2")
    opsgenie_target_team_name: str = os.getenv("OPSGENIE_TARGET_TEAM_NAME", "")
    
    squadcast_refresh_token: str = os.getenv("SQUADCAST_REFRESH_TOKEN", "")
    squadcast_region: str = os.getenv("SQUADCAST_REGION", "us")

    terraform_output_path: str = os.getenv("TERRAFORM_OUTPUT_PATH", "terraform_output")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")
