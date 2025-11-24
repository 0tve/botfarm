import enum
import pathlib

import pydantic

from botfarm.components import utils
from botfarm.entities import constants


class DBCredentialsEnvFields(enum.Enum):
    user = 'DB_USER'
    password = 'DB_PASSWORD'
    host = 'DB_HOST'
    port = 'DB_PORT'
    name_ = 'DB_NAME'

    @classmethod
    def get_name_field(cls) -> str:
        return cls.name_.name[:-1]


class DBDefaultCredentialsEnvFields(enum.Enum):
    user = 'DB_DEFAULT_USER'
    password = 'DB_DEFAULT_PASSWORD'
    host = 'DB_DEFAULT_HOST'
    port = 'DB_DEFAULT_PORT'
    name_ = 'DB_DEFAULT_NAME'

    @classmethod
    def get_name_field(cls) -> str:
        return cls.name_.name[:-1]


class DBCredentials(pydantic.BaseModel):
    user: str
    password: str
    host: str
    port: str
    name: str

    @property
    def url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'

    @classmethod
    def from_env_file(cls, env_path: pathlib.Path, fields: DBCredentialsEnvFields | DBDefaultCredentialsEnvFields) -> 'DBCredentials':
        env_vars = utils.load_env(env_path)
        try:
            return cls(
                user=env_vars[fields.user.value],
                password=env_vars[fields.password.value],
                host=env_vars[fields.host.value],
                port=env_vars[fields.port.value],
                name=env_vars[fields.name_.value],
            )
        except KeyError as exc:
            missing = exc.args[0]
            raise KeyError(f'Отсутствует ключ {missing} в {env_path}')


db_default_credentials = DBCredentials.from_env_file(
    pathlib.Path(constants.SETTINGS_FILE), DBDefaultCredentialsEnvFields)
db_credentials = DBCredentials.from_env_file(
    pathlib.Path(constants.SETTINGS_FILE), DBCredentialsEnvFields)
