import os
from datetime import date
from decimal import Decimal
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse


app = FastAPI(title="LetsFG Proxy", version="1.0.0")


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    expected_token = os.getenv("PROXY_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: PROXY_TOKEN is not set.",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer token.")

    provided_token = authorization.removeprefix("Bearer ").strip()
    if provided_token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token.")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search")
async def search(
    origin: str = Query(..., min_length=1),
    destination: str = Query(..., min_length=1),
    date_from: date = Query(...),
    date_to: date = Query(...),
    adults: int = Query(1, ge=1, le=9),
    max_price: Decimal | None = Query(None, ge=0),
    direct_only: bool = Query(False),
    _: None = Depends(require_bearer_token),
) -> JSONResponse:
    if date_to < date_from:
        raise HTTPException(status_code=422, detail="date_to must be on/after date_from.")

    letsfg_search_url = os.getenv("LETSFG_SEARCH_URL")
    if not letsfg_search_url:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: LETSFG_SEARCH_URL is not set.",
        )

    params: dict[str, Any] = {
        "origin": origin,
        "destination": destination,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "adults": adults,
        "direct_only": str(direct_only).lower(),
    }
    if max_price is not None:
        params["max_price"] = str(max_price)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            upstream_response = await client.get(letsfg_search_url, params=params)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream request failed: {exc.__class__.__name__}",
        ) from exc

    try:
        payload = upstream_response.json()
    except ValueError:
        payload = {"raw": upstream_response.text}

    return JSONResponse(
        status_code=upstream_response.status_code,
        content=payload,
    )
