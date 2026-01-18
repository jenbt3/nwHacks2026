from fastapi import FastAPI
from .db.database import engine, Base
from .core.websocket import manager
from .api import people, alerts, scripts

app = FastAPI(title="Cognitive Bridge API")

# Modular Routers - The single source of truth
app.include_router(people.router)
app.include_router(alerts.router)
app.include_router(scripts.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# The logic for /detect is now exclusively in scripts.py 
# to avoid 'Split Brain' behavior between Pi and Dashboard.