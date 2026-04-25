from unittest.mock import AsyncMock, patch

import pytest

from main import main, on_shutdown, on_startup


@pytest.mark.asyncio
async def test_on_startup():
    with patch("memory.database.Database.init_db", new_callable=AsyncMock):
        await on_startup()

@pytest.mark.asyncio
async def test_on_shutdown():
    with patch("memory.database.Database.close", new_callable=AsyncMock):
        with patch("core.bot.bot.session.close", new_callable=AsyncMock):
            await on_shutdown()

@pytest.mark.asyncio
async def test_main():
    with patch("core.bot.dp.start_polling", new_callable=AsyncMock) as mock_polling:
        await main()
        mock_polling.assert_called_once()
