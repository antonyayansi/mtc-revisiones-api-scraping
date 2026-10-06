from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.service import consultar_revisiones, normalize_placa

app = FastAPI(
    title="API Revisiones CITV",
    description="Consulta revisiones técnicas vehiculares (CITV) del MTC por placa.",
    version="1.0.0",
)


class ConsultaRequest(BaseModel):
    placa: str = Field(..., examples=["T2K867"], min_length=5, max_length=12)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/revisiones/{placa}")
def get_revisiones(placa: str) -> dict:
    return _consultar(placa)


@app.post("/revisiones")
def post_revisiones(body: ConsultaRequest) -> dict:
    return _consultar(body.placa)


@app.get("/revisiones")
def get_revisiones_query(placa: str = Query(..., min_length=5, max_length=12)) -> dict:
    return _consultar(placa)


def _consultar(placa: str) -> dict:
    try:
        normalize_placa(placa)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        return consultar_revisiones(placa)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}") from exc
