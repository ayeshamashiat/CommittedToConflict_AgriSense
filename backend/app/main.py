from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    calculate,
    chat,
    health,
    marketplace,
    payments,
    price_intelligence,
    disease_detection,
    retrieve,
    sessions,
    simulate,
    transcribe,
    weather,
)
from app.config import get_settings
from app.db.database import Base, SessionLocal, engine
from app.db.repositories.crop_reference_repo import seed_if_empty

settings = get_settings()

app = FastAPI(title="AgriSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # Vite picks the next free port (5174, 5175, ...) whenever 5173 is already
    # taken, which silently broke CORS since the allow-list only ever had the
    # default port hardcoded. Anything on localhost/127.0.0.1 during local dev
    # is trusted, regardless of which port it landed on.
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
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
app.include_router(marketplace.router)
app.include_router(payments.router)
app.include_router(price_intelligence.router)
app.include_router(disease_detection.router)
app.include_router(transcribe.router)
