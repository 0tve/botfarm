import sqlalchemy as sa
from sqlalchemy.ext import asyncio as sa_asyncio

from botfarm.entities import exceptions, models, schemas


async def _fetch_project(session: sa_asyncio.AsyncSession, name: str) -> models.Project | None:
    """Возвращает проект по его имени"""
    return await session.scalar(
        sa.select(models.Project).where(models.Project.name == name)
    )


async def get_project(name: str, session: sa_asyncio.AsyncSession) -> schemas.Project:
    """Возвращает проект по имени"""
    project = await _fetch_project(session, name)
    if project is None:
        raise exceptions.BotfarmProjectNotExistsError
    return schemas.Project.model_validate(project)


async def create_project(request: schemas.ProjectCreate, session: sa_asyncio.AsyncSession) -> schemas.Project:
    """Создает проект, если его еще нет"""
    project = await _fetch_project(session, request.name)
    if project is None:
        project = models.Project(name=request.name)
        session.add(project)
        await session.flush()
    await session.commit()
    await session.refresh(project)
    return schemas.Project.model_validate(project)


async def get_projects(limit: int, session: sa_asyncio.AsyncSession) -> list[schemas.Project]:
    """Возвращает список проектов"""
    result = await session.scalars(sa.select(models.Project).limit(limit))
    projects = result.all()
    return [schemas.Project.model_validate(project) for project in projects]


async def update_project(name: str, request: schemas.ProjectUpdate, session: sa_asyncio.AsyncSession) -> schemas.Project:
    """Обновляет данные проекта"""
    project = await _fetch_project(session, name)
    if project is None:
        raise exceptions.BotfarmProjectNotExistsError
    if request.name is not None:
        project.name = request.name
    await session.commit()
    await session.refresh(project)
    return schemas.Project.model_validate(project)


async def delete_project(name: str, session: sa_asyncio.AsyncSession) -> None:
    """Удаляет проект и обнуляет привязки пользователей к нему"""
    project = await _fetch_project(session, name)
    if project is None:
        raise exceptions.BotfarmProjectNotExistsError
    await session.execute(
        sa.update(models.User).where(models.User.project_id ==
                                     project.id).values(project_id=None)
    )
    await session.delete(project)
    await session.commit()
