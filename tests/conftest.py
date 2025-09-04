from __future__ import annotations

import httpx
import pytest
import pytest_asyncio

from tests.utils import FIXTURES_DIR


@pytest.fixture(autouse=True)
def manage_sys_path(monkeypatch):
    monkeypatch.syspath_prepend(FIXTURES_DIR)


@pytest_asyncio.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://nik.io") as client:
        yield client
