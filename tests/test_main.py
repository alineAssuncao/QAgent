import pytest
import asyncio
from main import on_startup, on_shutdown, main
from memory.database import Database

@pytest.mark.asyncio
async def test_on_startup():
    await on_startup()
    # Aqui você pode adicionar verificações para o que deve ter acontecido durante a inicialização

@pytest.mark.asyncio
async def test_on_shutdown():
    await on_shutdown()
    # Aqui você pode adicionar verificações para o que deve ter acontecido durante o encerramento

@pytest.mark.asyncio
async def test_main():
    await main()
