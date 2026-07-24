from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import calculate, chat, health, retrieve, sessions, simulate, weather
from app.config import get_settings
from app.db.database import Base, SessionLocal, engine
from app.db.repositories.crop_reference_repo import seed_if_empty

settings = get_settings()

app = FastAPI(title="AgriSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(retrieve.router)
app.include_router(calculate.router)
app.include_router(sessions.router)
app.include_router(simulate.router)
