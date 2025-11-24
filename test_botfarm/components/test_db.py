import asyncpg
import pytest

from botfarm.components import db
from botfarm.entities import exceptions


class DummySessionmaker:
    def __init__(self, *, execute_raises=None) -> None:
        self.execute_raises = execute_raises

    async def __aenter__(self) -> 'DummySessionmaker':
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return

    async def execute(self, _) -> None:
        if self.execute_raises:
            raise self.execute_raises


class DummyConn:
    def __init__(self) -> None:
        self.execution_options_called = False
        self.executed_statement = None

    async def execution_options(self, isolation_level) -> 'DummyConn':
        self.execution_options_called = True
        return self

    async def execute(self, statement) -> None:
        self.executed_statement = statement

    async def __aenter__(self) -> 'DummyConn':
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return


class DummyEngine:
    def __init__(self) -> None:
        self.conn = DummyConn()
        self.connect_called = False

    def connect(self) -> DummyConn:
        self.connect_called = True
        return self.conn


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'dummy_sessionmaker, exists',
    [
        pytest.param(lambda: DummySessionmaker(), True),
        pytest.param(lambda: DummySessionmaker(
            execute_raises=asyncpg.InvalidCatalogNameError()), False),
    ]
)
async def test_is_db_exists(dummy_sessionmaker, exists):
    assert await db.is_db_exists(dummy_sessionmaker) == exists


@pytest.mark.parametrize(
    'default_db_exists, db_exists',
    [
        pytest.param(False, False),
        pytest.param(True, False),
        pytest.param(False, True),
        pytest.param(True, True),
    ]
)
@pytest.mark.asyncio
async def test_ensure_db_exists(monkeypatch, default_db_exists, db_exists):
    default_marker = object()
    target_marker = object()
    calls = []

    async def mock_is_db_exists(sessionmaker):
        calls.append(sessionmaker)
        if sessionmaker is default_marker:
            return default_db_exists
        if sessionmaker is target_marker:
            return db_exists
        return False

    dummy_engine = DummyEngine()

    monkeypatch.setattr(db, 'is_db_exists', mock_is_db_exists)
    monkeypatch.setattr(db, 'async_default_engine', dummy_engine)
    monkeypatch.setattr(db, 'async_default_sessionmaker', default_marker)
    monkeypatch.setattr(db, 'async_sessionmaker', target_marker)

    should_raise = not default_db_exists and not db_exists
    if should_raise:
        with pytest.raises(exceptions.BotfarmDBError):
            await db.ensure_db_exists()
        assert dummy_engine.connect_called == False
        assert len(calls) == 2
        return

    await db.ensure_db_exists()

    assert len(calls) == 2
    if default_db_exists and not db_exists:
        assert dummy_engine.connect_called == True
        assert dummy_engine.conn.execution_options_called == True
        assert dummy_engine.conn.executed_statement is not None
    else:
        assert dummy_engine.connect_called == False
