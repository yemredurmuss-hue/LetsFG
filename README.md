# LetsFG Proxy (FastAPI)

A lightweight proxy API for LetsFG search calls, designed for easy deployment on Render Free.

## Features

- `GET /search` endpoint with query params:
  - `origin`
  - `destination`
  - `date_from` (YYYY-MM-DD)
  - `date_to` (YYYY-MM-DD)
  - `adults` (default `1`)
  - `max_price` (optional)
  - `direct_only` (default `false`)
- Bearer token protection via `PROXY_TOKEN`
- Forwards query params to LetsFG upstream URL

## Environment Variables

- `PROXY_TOKEN` (required): bearer token used by clients
- `LETSFG_SEARCH_URL` (required): upstream LetsFG search endpoint URL

Example:

```bash
PROXY_TOKEN=your-secret-token
LETSFG_SEARCH_URL=https://your-letsfg-endpoint/search
```

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PROXY_TOKEN="mytoken"
export LETSFG_SEARCH_URL="https://your-letsfg-endpoint/search"
uvicorn main:app --reload --host 0.0.0.0 --port 10000
```

## Request Example

```bash
curl -G "http://localhost:10000/search" \
  -H "Authorization: Bearer mytoken" \
  --data-urlencode "origin=IST" \
  --data-urlencode "destination=LHR" \
  --data-urlencode "date_from=2026-05-01" \
  --data-urlencode "date_to=2026-05-10" \
  --data-urlencode "adults=1" \
  --data-urlencode "max_price=300" \
  --data-urlencode "direct_only=true"
```

## Deploy on Render Free

1. Create a new **Web Service** from this repo.
2. Render should auto-detect `Dockerfile`.
3. Add environment variables:
   - `PROXY_TOKEN`
   - `LETSFG_SEARCH_URL`
4. Deploy.

The service listens on port `10000` inside the container.
