import fastapi

from botfarm.entities import schemas, models
from botfarm.components import users
from botfarm.components import projects


router = fastapi.APIRouter()


@router.post('/users')
async def create_user(request: schemas.UserCreate = fastapi.Depends()) -> schemas.User:
    return await users.create_user(request)


@router.get('/users')
async def get_users(
    limit: int = fastapi.Query(default=100, ge=1),
    project_name: str | None = fastapi.Query(default=None),
    domain: models.DomainType | None = fastapi.Query(default=None),
    env: models.EnvType | None = fastapi.Query(default=None),
) -> list[schemas.User]:
    return await users.get_users(limit, project_name=project_name, domain=domain, env=env)


@router.get('/users/{login}')
async def get_user(
    login: str,
    lock: bool = fastapi.Query(default=False),
) -> schemas.User:
    return await users.get_user(login, lock=lock)


@router.patch('/users/{login}')
async def update_user(login: str, request: schemas.UserUpdate = fastapi.Depends()) -> schemas.User:
    return await users.update_user(login, request)


@router.delete('/users/{login}', status_code=204)
async def delete_user(login: str) -> None:
    return await users.delete_user(login)


@router.post('/projects')
async def create_project(request: schemas.ProjectCreate = fastapi.Depends()) -> schemas.Project:
    return await projects.create_project(request)


@router.get('/projects')
async def list_projects(limit: int = fastapi.Query(default=100, ge=1)) -> list[schemas.Project]:
    return await projects.list_projects(limit)


@router.get('/projects/{name}')
async def get_project(name: str) -> schemas.Project:
    return await projects.get_project(name)


@router.patch('/projects/{name}')
async def update_project(name: str, request: schemas.ProjectUpdate = fastapi.Depends()) -> schemas.Project:
    return await projects.update_project(name, request)


@router.delete('/projects/{name}', status_code=204)
async def delete_project(name: str) -> None:
    return await projects.delete_project(name)
