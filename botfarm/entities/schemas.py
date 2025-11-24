from datetime import datetime
from uuid import UUID

import pydantic

from botfarm.entities import models


class ProjectCreate(pydantic.BaseModel):
    name: str


class Project(pydantic.BaseModel):
    id: UUID
    name: str

    model_config = pydantic.ConfigDict(from_attributes=True)

class ProjectUpdate(pydantic.BaseModel):
    name: str | None = None


class UserCreate(pydantic.BaseModel):
    login: str
    password: str
    project_name: str | None = None
    env: models.EnvType
    domain: models.DomainType

class UserUpdate(pydantic.BaseModel):
    password: str | None = None
    project_name: str | None = None
    env: models.EnvType | None = None
    domain: models.DomainType | None = None
    locktime: datetime | None = None


class User(pydantic.BaseModel):
    id: UUID
    created_at: datetime
    login: str
    project_id: UUID | None
    env: models.EnvType
    domain: models.DomainType
    locktime: datetime | None = None

    model_config = pydantic.ConfigDict(from_attributes=True)
