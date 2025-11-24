import types
import uuid

import pytest

from botfarm import api
from botfarm.entities import schemas


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


@pytest.mark.asyncio
async def test_create_project():
    calls = {'add': 0, 'commit': 0, 'refresh': 0, 'fetch': 0, 'flush': 0}

    class FakeSession:
        def __init__(self):
            self.last_added = None

        async def scalar(self, stmt):
            calls['fetch'] += 1
            return None

        def add(self, obj):
            calls['add'] += 1
            self.last_added = obj

        async def flush(self):
            calls['flush'] += 1
            if getattr(self.last_added, 'id', None) is None:
                self.last_added.id = uuid.uuid4()

        async def commit(self):
            calls['commit'] += 1

        async def refresh(self, obj):
            calls['refresh'] += 1

    fake_session = FakeSession()
    request = schemas.ProjectCreate(name='proj')

    result = await api.create_project(request=request, session=fake_session)

    assert result.name == 'proj'
    assert calls == {'add': 1, 'commit': 1, 'refresh': 1, 'fetch': 1, 'flush': 1}


@pytest.mark.asyncio
async def test_get_projects():
    class FakeSession:
        def __init__(self):
            self.scalars_calls = 0

        async def scalars(self, stmt):
            self.scalars_calls += 1
            return FakeScalarResult([
                types.SimpleNamespace(id=uuid.uuid4(), name='p1'),
                types.SimpleNamespace(id=uuid.uuid4(), name='p2'),
            ])

    fake_session = FakeSession()
    result = await api.get_projects(limit=2, session=fake_session)

    assert fake_session.scalars_calls == 1
    assert len(result) == 2
    assert all(isinstance(item, schemas.Project) for item in result)


@pytest.mark.asyncio
async def test_get_project():
    class FakeSession:
        def __init__(self):
            self.calls = 0

        async def scalar(self, stmt):
            self.calls += 1
            return types.SimpleNamespace(id=uuid.uuid4(), name='proj')

    fake_session = FakeSession()
    result = await api.get_project(name='proj', session=fake_session)
    assert fake_session.calls == 1
    assert result.name == 'proj'


@pytest.mark.asyncio
async def test_update_project():
    class FakeSession:
        def __init__(self):
            self.scalar_calls = 0
            self.commit_calls = 0
            self.refresh_calls = 0
            self.project = types.SimpleNamespace(id=uuid.uuid4(), name='old')

        async def scalar(self, stmt):
            self.scalar_calls += 1
            return self.project

        async def commit(self):
            self.commit_calls += 1

        async def refresh(self, obj):
            self.refresh_calls += 1

    fake_session = FakeSession()
    request = schemas.ProjectUpdate(name='new')
    result = await api.update_project(name='old', request=request, session=fake_session)

    assert fake_session.scalar_calls == 1
    assert fake_session.commit_calls == 1
    assert fake_session.refresh_calls == 1
    assert result.name == 'new'


@pytest.mark.asyncio
async def test_delete_project():
    class FakeSession:
        def __init__(self):
            self.scalar_calls = 0
            self.commit_calls = 0
            self.execute_calls = 0
            self.delete_calls = 0
            self.project = types.SimpleNamespace(id=uuid.uuid4(), name='proj')

        async def scalar(self, stmt):
            self.scalar_calls += 1
            return self.project

        async def execute(self, stmt):
            self.execute_calls += 1

        async def delete(self, obj):
            self.delete_calls += 1

        async def commit(self):
            self.commit_calls += 1

    fake_session = FakeSession()
    result = await api.delete_project(name='proj', session=fake_session)

    assert result is None
    assert fake_session.scalar_calls == 1
    assert fake_session.execute_calls == 1
    assert fake_session.delete_calls == 1
    assert fake_session.commit_calls == 1
