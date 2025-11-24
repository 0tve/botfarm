import pathlib

import pytest

DB_USER = 'user'
DB_PASSWORD = 'password'
DB_HOST = 'host'
DB_PORT = '1'
DB_NAME = 'name'


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
