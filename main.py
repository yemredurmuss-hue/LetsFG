import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROXY_TOKEN = os.getenv("PROXY_TOKEN", "letsfg123")
LETSFG_API_KEY = os.getenv("LETSFG_API_KEY", "")

@app.get("/search")
async def search(
    origin: str,
    destination: str,
    date: str,
    adults: int = 1,
    cabin: str = "economy",
    authorization: str = Header(None)
):
    token = (authorization or "").replace("Bearer ", "")
    if token != PROXY_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            "https://api.letsfg.co/v1/flights/search",
            params={
                "origin": origin,
                "destination": destination,
                "departure_date": date,
                "adults": adults,
                "cabin_class": cabin,
            },
            headers={"X-API-Key": LETSFG_API_KEY}  # ← Düzeltildi!
        )
    return r.json()

@app.get("/health")
async def health():
    return {"status": "ok"}
