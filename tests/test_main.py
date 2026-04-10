import pytest
from unittest.mock import patch
from main import on_startup, on_shutdown

@pytest.fixture
def mock_database():
    with patch('memory.database.Database') as mock_db:
        yield mock_db

async def test_on_startup(mock_database):
    await on_startup()
    mock_database.init_db.assert_awaited()

async def test_on_shutdown(mock_database):
    await on_shutdown()
    mock_database.close.assert_awaited()
    assert mock_database.session.close.called