# main.py
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.configs import settings
from app.database import get_db_route

app = FastAPI(title="Dynamic Multi-DB Backend")


@app.get("/", include_in_schema=False)
def root():
    return {"app": app.title, "docs": "/docs", "endpoints": ["/db-health", "/query-data"]}


@app.get("/db-health")
def health(db: Session = Depends(get_db_route)):
    """Verifies the selected database is reachable (SELECT 1)."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/query-data")
def read_data(db: Session = Depends(get_db_route)):
    # Runs against either PostgreSQL or Databricks depending on the routing condition
    try:
        # Table name comes from config (not user input), so it is safe to interpolate.
        query = text(f"SELECT * FROM {settings.sample_table} LIMIT 5")
        rows = [dict(row) for row in db.execute(query).mappings().all()]
        return {"status": "success", "data": rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
