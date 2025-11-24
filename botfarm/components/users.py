from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.ext import asyncio as sa_asyncio

from botfarm.components import projects, utils
from botfarm.entities import exceptions, models, schemas


async def _fetch_user(session: sa_asyncio.AsyncSession, login: str) -> models.User | None:
    """Возвращает пользователя по логину"""
    return await session.scalar(
        sa.select(models.User).where(models.User.login == login)
    )


async def create_user(request: schemas.UserCreate, session: sa_asyncio.AsyncSession) -> schemas.User:
    """Создает нового пользователя, привязывая к проекту, если он указан"""
    project_id = None
    if request.project_name is not None:
        project = await projects.get_project(request.project_name, session=session)
        project_id = project.id
    user = models.User(
        login=request.login,
        password=utils.hash_password(request.password),
        project_id=project_id,
        env=request.env,
        domain=request.domain,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return schemas.User.model_validate(user)


async def get_users(
    limit: int,
    session: sa_asyncio.AsyncSession,
    project_name: str | None = None,
    domain: models.DomainType | None = None,
    env: models.EnvType | None = None,
) -> list[schemas.User]:
    """Возвращает список пользователей, который матчится с указанными фильтрами"""
    statement = sa.select(models.User)
    if project_name is not None:
        project = await session.scalar(
            sa.select(models.Project).where(
                models.Project.name == project_name)
        )
        if project is None:
            raise exceptions.BotfarmProjectNotExistsError
        statement = statement.where(models.User.project_id == project.id)
    if domain is not None:
        statement = statement.where(models.User.domain == domain)
    if env is not None:
        statement = statement.where(models.User.env == env)
    result = await session.scalars(statement.limit(limit))
    users = result.all()
    return [schemas.User.model_validate(user) for user in users]


async def get_user(login: str, session: sa_asyncio.AsyncSession, lock: bool = False) -> schemas.User:
    """Возвращает пользователя по логину и блокирует его, если lock равен True"""
    if lock:
        return await acquire_lock(login, session=session)
    user = await _fetch_user(session, login)
    if user is None:
        raise exceptions.BotfarmUserNotExistsError
    if user.locktime is not None:
        raise exceptions.BotfarmUserLockedError
    return schemas.User.model_validate(user)


async def acquire_lock(login: str, session: sa_asyncio.AsyncSession) -> schemas.User:
    """Ставит блокировку на пользователя"""
    user = await _fetch_user(session, login)
    if user is None:
        raise exceptions.BotfarmUserNotExistsError
    if user.locktime is not None:
        raise exceptions.BotfarmUserLockedError
    user.locktime = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(user)
    return schemas.User.model_validate(user)


async def release_lock(login: str, session: sa_asyncio.AsyncSession) -> schemas.User:
    """Снимает блокировку с пользователя"""
    user = await _fetch_user(session, login)
    if user is None:
        raise exceptions.BotfarmUserNotExistsError
    user.locktime = None
    await session.commit()
    await session.refresh(user)
    return schemas.User.model_validate(user)


async def update_user(login: str, request: schemas.UserUpdate, session: sa_asyncio.AsyncSession) -> schemas.User:
    """Обновляет данные пользователя"""
    user = await _fetch_user(session, login)
    if user is None:
        raise exceptions.BotfarmUserNotExistsError

    if request.project_name is not None:
        if request.project_name == '':
            user.project_id = None
        else:
            project = await session.scalar(
                sa.select(models.Project).where(
                    models.Project.name == request.project_name)
            )
            if project is None:
                raise exceptions.BotfarmProjectNotExistsError
            user.project_id = project.id
    if request.password is not None:
        user.password = utils.hash_password(request.password)
    if request.env is not None:
        user.env = request.env
    if request.domain is not None:
        user.domain = request.domain
    if request.locktime is not None:
        user.locktime = request.locktime

    await session.commit()
    await session.refresh(user)
    return schemas.User.model_validate(user)


async def delete_user(login: str, session: sa_asyncio.AsyncSession) -> None:
    """Удаляет пользователя"""
    user = await _fetch_user(session, login)
    if user is None:
        raise exceptions.BotfarmUserNotExistsError
    await session.delete(user)
    await session.commit()
