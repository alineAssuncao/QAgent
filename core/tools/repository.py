import os
import logging
from typing import Dict, Any, List, Optional
from core.tools.base import BaseTool
from core.config import settings


class ListDirectoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "Lista arquivos e pastas em um diretório específico do projeto para entender a estrutura."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho relativo ao diretório raiz do projeto (ex: '.', 'src/').",
                }
            },
            "required": ["path"],
        }

    async def execute(self, path: str = ".", **kwargs) -> str:
        full_path = os.path.join(settings.BASE_DIR, path)
        try:
            if not os.path.exists(full_path):
                return f"Erro: O caminho '{path}' não existe."

            items = os.listdir(full_path)
            result = []
            for item in items:
                item_path = os.path.join(full_path, item)
                is_dir = os.path.isdir(item_path)
                result.append(f"{'[DIR] ' if is_dir else '[FILE]'} {item}")

            return "\n".join(result) if result else "Diretório vazio."
        except Exception as e:
            return f"Erro ao listar diretório: {str(e)}"


class ReadFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Lê o conteúdo de um arquivo específico para análise de código ou testes."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho relativo do arquivo (ex: 'main.py').",
                }
            },
            "required": ["path"],
        }

    async def execute(self, path: str) -> str:
        full_path = os.path.join(settings.BASE_DIR, path)
        try:
            if not os.path.exists(full_path):
                return f"Erro: O arquivo '{path}' não existe."

            if os.path.isdir(full_path):
                return f"Erro: '{path}' é um diretório, use list_directory."

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Limite de segurança para 10k caracteres para evitar estouro de contexto
                if len(content) > 10000:
                    return (
                        content[:10000]
                        + "\n\n...[Conteúdo truncado por limite de tamanho]..."
                    )
                return content
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"


class WriteFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Escreve ou cria um novo arquivo com o conteúdo especificado."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho relativo do arquivo a ser criado (ex: 'src/test_main.py').",
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo a ser escrito no arquivo.",
                },
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str) -> str:
        full_path = os.path.join(settings.BASE_DIR, path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ Arquivo criado: {path}"
        except Exception as e:
            return f"Erro ao escrever arquivo: {str(e)}"
