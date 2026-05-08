from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_reports import router as reports_router
from app.config import settings
from app.db.models import Report, RunEvent
from app.db.session import Base, engine

app = FastAPI(title="HV Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine, tables=[Report.__table__, RunEvent.__table__])
app.include_router(reports_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
