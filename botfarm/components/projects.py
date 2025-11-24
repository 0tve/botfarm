import sqlalchemy as sa
from sqlalchemy.ext import asyncio as sa_asyncio

from botfarm.components import db
from botfarm.entities import models
from botfarm.entities import schemas
from botfarm.entities import exceptions


async def _fetch_project(session: sa_asyncio.AsyncSession, name: str) -> models.Project | None:
    return await session.scalar(
        sa.select(models.Project).where(models.Project.name == name)
    )


async def get_project(name: str) -> schemas.Project:
    async with db.async_sessionmaker() as session:
        project = await _fetch_project(session, name)
        if project is None:
            raise exceptions.BotfarmProjectNotExistsError
        return schemas.Project.model_validate(project)


async def create_project(request: schemas.ProjectCreate) -> schemas.Project:
    async with db.async_sessionmaker() as session:
        project = await _fetch_project(session, request.name)
        if project is None:
            project = models.Project(name=request.name)
            session.add(project)
            await session.flush()
        await session.commit()
        await session.refresh(project)
        return schemas.Project.model_validate(project)


async def list_projects(limit: int) -> list[schemas.Project]:
    async with db.async_sessionmaker() as session:
        result = await session.scalars(sa.select(models.Project).limit(limit))
        projects = result.all()
        return [schemas.Project.model_validate(project) for project in projects]


async def update_project(name: str, request: schemas.ProjectUpdate) -> schemas.Project:
    async with db.async_sessionmaker() as session:
        project = await _fetch_project(session, name)
        if project is None:
            raise exceptions.BotfarmProjectNotExistsError
        if request.name is not None:
            project.name = request.name
        await session.commit()
        await session.refresh(project)
        return schemas.Project.model_validate(project)


async def delete_project(name: str) -> None:
    async with db.async_sessionmaker() as session:
        project = await _fetch_project(session, name)
        if project is None:
            raise exceptions.BotfarmProjectNotExistsError
        await session.execute(
            sa.update(models.User).where(models.User.project_id ==
                                         project.id).values(project_id=None)
        )
        await session.delete(project)
        await session.commit()
