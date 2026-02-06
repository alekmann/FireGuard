from fastapi import FastAPI
from app.firebase import init_firebase
from app.api import router as api_router
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="FireGuard API")

# Init Firebase only when app starts (not during tests)
init_firebase()

app.include_router(api_router)
