import types
import uuid
from datetime import datetime, timezone

import pytest

from botfarm import api
from botfarm.components import projects, utils
from botfarm.entities import exceptions, models, schemas
from test_botfarm.conftest import MockScalarResult


class MockSession:
    """Моковая сессия, которая считает вызовы add/commit/refresh"""

    def __init__(self):
        self.add_count = 0
        self.commit_count = 0
        self.refresh_count = 0
        self.last_added = None

    def add(self, obj):
        self.add_count += 1
        self.last_added = obj
        if getattr(obj, 'id', None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, 'created_at', None) is None:
            obj.created_at = datetime.now(timezone.utc)
        if getattr(obj, 'locktime', None) is None:
            obj.locktime = None

    async def commit(self):
        self.commit_count += 1

    async def refresh(self, obj):
        self.refresh_count += 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload, expected_project_id, expected_project_calls',
    [
        pytest.param(
            {
                'login': 'user@example.com',
                'password': 'password',
                'env': models.EnvType.prod,
                'domain': models.DomainType.regular,
                'project_name': None,
            },
            None,
            0,
        ),
        pytest.param(
            {
                'login': 'user2@example.com',
                'password': 'password2',
                'env': models.EnvType.stage,
                'domain': models.DomainType.canary,
                'project_name': 'proj',
            },
            uuid.uuid4(),
            1,
        ),
    ],
)
async def test_create_user(payload, expected_project_id, expected_project_calls, monkeypatch):
    mock_session = MockSession()
    calls = {'projects': 0}

    async def mock_get_project(name, session):
        calls['projects'] += 1
        assert name == payload['project_name']
        assert session is mock_session
        return types.SimpleNamespace(id=expected_project_id)

    monkeypatch.setattr(projects, 'get_project', mock_get_project)

    request = schemas.UserCreate(**payload)
    result = await api.create_user(request=request, session=mock_session)

    assert calls['projects'] == expected_project_calls
    assert mock_session.add_count == 1
    assert mock_session.commit_count == 1
    assert mock_session.refresh_count == 1

    assert result.login == request.login
    assert result.project_id == expected_project_id
    assert result.env == request.env
    assert result.domain == request.domain
    assert result.locktime is None
    assert mock_session.last_added.password == utils.hash_password(request.password)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'project_name, project_obj, expected_scalar_calls',
    [
        pytest.param(None, None, 0),
        pytest.param('project', types.SimpleNamespace(id=uuid.uuid4()), 1),
    ],
)
async def test_get_users(project_name, project_obj, expected_scalar_calls, limit_two):
    class MockSessionForGetUsers:
        def __init__(self):
            self.scalar_calls = []
            self.scalars_calls = []

        async def scalar(self, stmt):
            self.scalar_calls.append(stmt)
            return project_obj

        async def scalars(self, stmt):
            self.scalars_calls.append(stmt)
            return MockScalarResult(mock_users)

    mock_session = MockSessionForGetUsers()

    mock_users = [
        types.SimpleNamespace(
            id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            login='u1@example.com',
            project_id=project_obj.id if project_obj else None,
            env=models.EnvType.prod,
            domain=models.DomainType.regular,
            locktime=None,
        ),
        types.SimpleNamespace(
            id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            login='u2@example.com',
            project_id=project_obj.id if project_obj else None,
            env=models.EnvType.prod,
            domain=models.DomainType.regular,
            locktime=None,
        ),
    ]

    result = await api.get_users(
        limit=limit_two,
        project_name=project_name,
        domain=models.DomainType.regular,
        env=models.EnvType.prod,
        session=mock_session,
    )

    assert len(mock_session.scalar_calls) == expected_scalar_calls
    assert len(mock_session.scalars_calls) == 1
    stmt = mock_session.scalars_calls[0]
    assert 'LIMIT' in str(stmt)
    compiled_params = stmt.compile().params
    assert limit_two in compiled_params.values()

    assert len(result) == len(mock_users)
    assert all(isinstance(item, schemas.User) for item in result)
    assert all(item.domain == models.DomainType.regular for item in result)
    assert all(item.env == models.EnvType.prod for item in result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'lock_flag, initial_locktime, expect_commit, expect_refresh, expect_exception',
    [
        pytest.param(False, None, 0, 0, None),
        pytest.param(True, None, 1, 1, None),
        pytest.param(False, datetime.now(timezone.utc), 0, 0, exceptions.BotfarmUserLockedError),
    ],
)
async def test_get_user(lock_flag, initial_locktime, expect_commit, expect_refresh, expect_exception):
    class MockSession:
        def __init__(self):
            self.scalar_calls = 0
            self.commit_count = 0
            self.refresh_count = 0

        async def scalar(self, stmt):
            self.scalar_calls += 1
            return types.SimpleNamespace(
                id=uuid.uuid4(),
                created_at=datetime.now(timezone.utc),
                login='user@example.com',
                password='hash',
                project_id=None,
                env=models.EnvType.prod,
                domain=models.DomainType.regular,
                locktime=initial_locktime,
            )

        async def commit(self):
            self.commit_count += 1

        async def refresh(self, obj):
            self.refresh_count += 1

    mock_session = MockSession()

    if expect_exception:
        with pytest.raises(expect_exception):
            await api.get_user(login='user@example.com', lock=lock_flag, session=mock_session)
        return

    result = await api.get_user(login='user@example.com', lock=lock_flag, session=mock_session)

    assert mock_session.scalar_calls == 1
    assert mock_session.commit_count == expect_commit
    assert mock_session.refresh_count == expect_refresh
    assert result.login == 'user@example.com'
    assert result.project_id is None
    assert result.env == models.EnvType.prod
    assert result.domain == models.DomainType.regular
    if lock_flag:
        assert result.locktime is not None
    else:
        assert result.locktime is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload, project_obj, expected_project_calls',
    [
        pytest.param(
            {
                'password': 'newpass',
                'project_name': None,
                'env': models.EnvType.stage,
                'domain': models.DomainType.canary,
                'locktime': None,
            },
            None,
            0,
        ),
        pytest.param(
            {
                'password': 'another',
                'project_name': 'proj',
                'env': models.EnvType.prod,
                'domain': models.DomainType.regular,
                'locktime': datetime.now(timezone.utc),
            },
            types.SimpleNamespace(id=uuid.uuid4()),
            1,
        ),
    ],
)
async def test_update_user(payload, project_obj, expected_project_calls, monkeypatch):
    calls = {'scalar': 0, 'project': 0, 'commit': 0, 'refresh': 0}

    class MockSession:
        def __init__(self):
            self.user = types.SimpleNamespace(
                id=uuid.uuid4(),
                created_at=datetime.now(timezone.utc),
                login='user@example.com',
                password='old',
                project_id=None,
                env=models.EnvType.prod,
                domain=models.DomainType.regular,
                locktime=None,
            )

        async def scalar(self, stmt):
            calls['scalar'] += 1
            if calls['scalar'] == 1 and 'projects' in str(stmt):
                calls['project'] += 1
                return project_obj
            if calls['scalar'] == 1:
                return self.user
            if calls['scalar'] == 2 and payload['project_name'] is not None:
                calls['project'] += 1
                return project_obj
            return self.user

        async def commit(self):
            calls['commit'] += 1

        async def refresh(self, _):
            calls['refresh'] += 1

    async def mock_get_project(name, session):
        calls['project'] += 1
        assert session is mock_session
        assert name == payload['project_name']
        return project_obj

    mock_session = MockSession()

    if payload['project_name'] is not None:
        monkeypatch.setattr(projects, 'get_project', mock_get_project)

    request = schemas.UserUpdate(**payload)
    result = await api.update_user(login='user@example.com', request=request, session=mock_session)

    assert calls['commit'] == 1
    assert calls['refresh'] == 1
    assert calls['scalar'] >= 1
    assert calls['project'] == expected_project_calls

    assert result.login == 'user@example.com'
    assert result.project_id == (project_obj.id if project_obj else None)
    assert result.env == payload['env']
    assert result.domain == payload['domain']
    assert result.locktime == payload['locktime']


@pytest.mark.asyncio
async def test_delete_user():
    calls = {'scalar': 0, 'delete': 0, 'commit': 0}

    class MockSession:
        def __init__(self):
            self.user = types.SimpleNamespace(id=uuid.uuid4())

        async def scalar(self, stmt):
            calls['scalar'] += 1
            return self.user

        async def delete(self, obj):
            calls['delete'] += 1
            assert obj is self.user

        async def commit(self):
            calls['commit'] += 1

    mock_session = MockSession()

    result = await api.delete_user(login='user@example.com', session=mock_session)

    assert result is None
    assert calls['scalar'] == 1
    assert calls['delete'] == 1
    assert calls['commit'] == 1
