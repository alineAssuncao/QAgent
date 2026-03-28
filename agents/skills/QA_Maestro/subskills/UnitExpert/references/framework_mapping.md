# 🛠️ Mapeamento de Linguagens para Frameworks (UnitExpert)

Este guia ajuda a **UnitExpert** a identificar a linguagem de programação e sugerir o framework de teste unitário mais adequado, alinhado aos padrões da indústria.

---

## 🏛️ Tabela de Referência

| Linguagem | Extensão | Framework Recomendado | Comando de Execução (Exemplo) |
| :--- | :--- | :--- | :--- |
| **Python** | `.py` | `pytest` | `pytest <arquivo_de_teste>.py` |
| **JavaScript/TypeScript** | `.js`, `.ts` | `jest` / `vitest` | `npm test` ou `vitest run` |
| **Java** | `.java` | `JUnit 5` | `mvn test` ou `gradle test` |
| **C#** | `.cs` | `xUnit` / `NUnit` | `dotnet test` |
| **Go** | `.go` | `testing` (padrão) | `go test ./...` |
| **Ruby** | `.rb` | `RSpec` | `rspec spec/` |
| **PHP** | `.php` | `PHPUnit` | `./vendor/bin/phpunit` |
| **C++** | `.cpp` | `GoogleTest` | `ctest` |

---

## 🔍 Como identificar o ambiente?

1.  **Arquivos de Configuração**:
    -   `pyproject.toml`, `requirements.txt` -> Python/Pytest
    -   `package.json` -> Node.js/Jest/Vitest
    -   `pom.xml`, `build.gradle` -> Java/JUnit
    -   `.csproj` -> .NET/xUnit

2.  **Contexto do Projeto**:
    -   Verificar diretórios como `tests/`, `__tests__` ou sufixos como `.spec.js`, `_test.go`.

---

## 💡 Sugestão Dinâmica

-   **Prioridade 1**: Usar o framework já configurado no projeto (ex: se `package.json` listar `vitest`, use Vitest).
-   **Prioridade 2**: Se não houver configuração, sugerir o padrão mais moderno para a linguagem (ex: `pytest` para Python).
-   **Prioridade 3**: Para scripts isolados, sugerir o framework que ofereça o melhor suporte a mocks sem configuração complexa.
