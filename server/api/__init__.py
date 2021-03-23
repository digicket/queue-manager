# API Router Initialization
from fastapi import APIRouter, FastAPI

from server.api.endpoints.message import router

app = FastAPI()
app.include_router(router, prefix='/api/v1/publisher')