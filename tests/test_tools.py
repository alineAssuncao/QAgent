from typing import Any, Dict

import pytest

from core.tools.base import BaseTool
from core.tools.git import CloneRepositoryTool
from core.tools.manager import ToolManager


class MockTool(BaseTool):
    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "Uma ferramenta de teste"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"input": {"type": "string"}},
            "required": ["input"],
        }

    async def execute(self, **kwargs) -> str:
        return f"Executado com: {kwargs.get('input', 'nada')}"


class TestToolManager:
    def test_get_tool_definitions(self):
        tools = [MockTool()]
        manager = ToolManager(tools)

        definitions = manager.get_tool_definitions()
        assert "mock_tool" in definitions
        assert "Uma ferramenta de teste" in definitions

    def test_get_tool_definitions_empty(self):
        manager = ToolManager([])
        definitions = manager.get_tool_definitions()
        assert "Nenhuma ferramenta disponível" in definitions

    @pytest.mark.asyncio
    async def test_call_tool_existing(self):
        tools = [MockTool()]
        manager = ToolManager(tools)

        result = await manager.call_tool("mock_tool", {"input": "teste"})
        assert "Executado com: teste" in result

    @pytest.mark.asyncio
    async def test_call_tool_not_found(self):
        manager = ToolManager([])

        result = await manager.call_tool("inexistente", {})
        assert "não encontrada" in result

    @pytest.mark.asyncio
    async def test_call_tool_error(self):
        class BrokenTool(BaseTool):
            @property
            def name(self) -> str:
                return "broken"

            @property
            def description(self) -> str:
                return "Quebrada"

            async def execute(self, **kwargs) -> str:
                raise ValueError("Erro intencional")

        manager = ToolManager([BrokenTool()])
        result = await manager.call_tool("broken", {})
        assert "Erro" in result


class TestCloneRepositoryTool:
    @property
    def parameters(self):
        tool = CloneRepositoryTool()
        return tool.parameters

    def test_parameters_structure(self):
        params = self.parameters
        assert "type" in params
        assert "properties" in params
        assert "url" in params["properties"]
        assert "folder_name" in params["properties"]
        assert "url" in params["required"]

    def test_name(self):
        tool = CloneRepositoryTool()
        assert tool.name == "clone_repository"

    def test_description(self):
        tool = CloneRepositoryTool()
        assert "Clona um repositório Git" in tool.description
