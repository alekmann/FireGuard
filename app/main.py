from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.firebase import init_firebase
from app.api import router as api_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    yield


app = FastAPI(
    title="FireGuard API",
    lifespan=lifespan,
)

app.include_router(api_router)
