# stock_api (FastAPI + AkShare)

## Run (Dev)
```bash
cd api/stock_api
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
