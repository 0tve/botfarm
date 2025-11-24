import fastapi
from sqlalchemy.ext import asyncio as sa_asyncio

from botfarm.components import db, projects, users
from botfarm.entities import models, schemas

router = fastapi.APIRouter()


@router.post('/users')
async def create_user(
    request: schemas.UserCreate = fastapi.Depends(),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> schemas.User:
    return await users.create_user(request, session=session)


@router.get('/users')
async def get_users(
    limit: int = fastapi.Query(default=100, ge=1),
    project_name: str | None = fastapi.Query(default=None),
    domain: models.DomainType | None = fastapi.Query(default=None),
    env: models.EnvType | None = fastapi.Query(default=None),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> list[schemas.User]:
    return await users.get_users(limit, project_name=project_name, domain=domain, env=env, session=session)


@router.get('/users/{login}')
async def get_user(
    login: str,
    lock: bool = fastapi.Query(default=False),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> schemas.User:
    return await users.get_user(login, lock=lock, session=session)


@router.patch('/users/{login}')
async def update_user(
    login: str,
    request: schemas.UserUpdate = fastapi.Depends(),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> schemas.User:
    return await users.update_user(login, request, session=session)


@router.delete('/users/{login}', status_code=204)
async def delete_user(
    login: str,
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> None:
    return await users.delete_user(login, session=session)


@router.post('/projects')
async def create_project(
    request: schemas.ProjectCreate = fastapi.Depends(),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> schemas.Project:
    return await projects.create_project(request, session=session)


@router.get('/projects')
async def get_projects(
    limit: int = fastapi.Query(default=100, ge=1),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> list[schemas.Project]:
    return await projects.get_projects(limit, session=session)


@router.get('/projects/{name}')
async def get_project(name: str, session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session)) -> schemas.Project:
    return await projects.get_project(name, session=session)


@router.patch('/projects/{name}')
async def update_project(
    name: str,
    request: schemas.ProjectUpdate = fastapi.Depends(),
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> schemas.Project:
    return await projects.update_project(name, request, session=session)


@router.delete('/projects/{name}', status_code=204)
async def delete_project(
    name: str,
    session: sa_asyncio.AsyncSession = fastapi.Depends(db.get_session),
) -> None:
    return await projects.delete_project(name, session=session)
