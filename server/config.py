# Configurations - Set environment variables to change

from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str = '127.0.0.1'
    PORT: int = 8000
    QUEUE_URL: str = '<REPLACEME>'
    QUEUE_REGION: str = 'us-west-2'
    DEV_ENABLED: bool = False
    AWS_ACCESS_KEY_ID: str = '<REPLACEME>'
    AWS_SECRET_ACCESS_KEY: str = '<REPLACEME>'


settings = Settings()
