# Configurations - Set environment variables to change

from pydantic import BaseSettings


class Settings(BaseSettings):
    QUEUE_URL: str = '<REPLACEME>'
    QUEUE_REGION: str = 'us-west-2'
    QUEUE_WAIT_TIME: int = 5
    MAX_NUMBER_OF_MESSAGES: int = 10
    DEV_ENABLED: bool = False
    MAX_THREADS: int = 10
    AWS_ACCESS_KEY_ID: str = '<REPLACEME>'
    AWS_SECRET_ACCESS_KEY: str = '<REPLACEME>'


settings = Settings()
