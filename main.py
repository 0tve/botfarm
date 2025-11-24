from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from botfarm.components import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.ensure_db_exists()
    await db.create_tables()
    yield
  
app = FastAPI(lifespan=lifespan)

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)