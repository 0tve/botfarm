import pathlib
import types
import uuid
from datetime import datetime, timezone

import pytest

DB_USER = 'user'
DB_PASSWORD = 'password'
DB_HOST = 'host'
DB_PORT = '1'
DB_NAME = 'name'


class MockScalarResult:
    """Мок scalars().all()"""

    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


@pytest.fixture
def make_mock_user():
    def _make(login='user@example.com', project_id=None, env='prod', domain='regular', locktime=None, password='hash'):
        return types.SimpleNamespace(
            id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            login=login,
            password=password,
            project_id=project_id,
            env=env,
            domain=domain,
            locktime=locktime,
        )
    return _make


@pytest.fixture
def make_mock_project():
    def _make(name='proj', project_id=None):
        return types.SimpleNamespace(
            id=project_id or uuid.uuid4(),
            name=name,
        )
    return _make


@pytest.fixture
def limit_two():
    return 2


@pytest.fixture
def get_file_path(request: pytest.FixtureRequest) -> pathlib.Path:
    base_dir = pathlib.Path(request.node.fspath).parent

    def _find(file_name: str) -> pathlib.Path:
        path = pathlib.Path(file_name)
        if not path.is_absolute():
            path = base_dir / path
        path = path.resolve()
        return path

    return _find
