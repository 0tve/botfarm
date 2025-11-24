import enum
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql as pg


class Base(orm.DeclarativeBase):
    pass


class EnvType(enum.Enum):
    prod = 'prod'
    preprod = 'preprod'
    stage = 'stage'


class DomainType(enum.Enum):
    canary = 'canary'
    regular = 'regular'


class User(Base):
    """Сущность пользователя.

    Args:
        id: UUID пользователя
        created_at: дата создания пользователя
        login: почтовый адрес пользователя
        password: пароль пользователя в зашифрованном виде
        project_id: UUID проекта, к которому принадлежит пользователь
        env: название окружения (prod, preprod, stage)
        domain: тип пользователя (canary, regular)
        locktime: временная метка (timestamp)
    """
    __tablename__ = 'users'

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False,
    )
    login: orm.Mapped[str] = orm.mapped_column(
        sa.String(255), nullable=False, unique=True)
    password: orm.Mapped[str] = orm.mapped_column(
        sa.String(255), nullable=False)
    project_id: orm.Mapped[uuid.UUID | None] = orm.mapped_column(
        pg.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True
    )
    env: orm.Mapped[EnvType] = orm.mapped_column(
        sa.Enum(EnvType, name='env_type'), nullable=False
    )
    domain: orm.Mapped[DomainType] = orm.mapped_column(
        sa.Enum(DomainType, name='domain_type'), nullable=False
    )
    locktime: orm.Mapped[datetime | None] = orm.mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )


class Project(Base):
    """Сущность проекта.

    Args:
        id: UUID проекта
        name: название проекта
    """
    __tablename__ = 'projects'

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: orm.Mapped[str] = orm.mapped_column(
        sa.String(255), nullable=False, unique=True)
