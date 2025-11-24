from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from botfarm import api
from botfarm.components import db, exceptions
from botfarm.entities import exceptions as exception_entities


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.ensure_db_exists()
    await db.create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api.router)
app.add_exception_handler(exception_entities.BotfarmProjectNotExistsError,
                          exceptions.handle_project_not_exists_error)
app.add_exception_handler(
    exception_entities.BotfarmUserNotExistsError, exceptions.handle_user_not_exists_error)
app.add_exception_handler(
    exception_entities.BotfarmUserLockedError, exceptions.handle_user_locked_error)

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)
