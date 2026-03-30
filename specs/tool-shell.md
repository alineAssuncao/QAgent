# Spec: Tool — RunShellTool (Execução Controlada de Comandos)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** QAgent Team
**Data:** 2026-03-29

---

## 1. Resumo

A **RunShellTool** é a ferramenta que permite ao QAgent executar comandos de terminal de forma segura e controlada. Utiliza uma **whitelist estrita** de comandos permitidos, sanitização de inputs contra injeção, e remoção de variáveis sensíveis do ambiente do subprocesso.

---

## 2. Contexto e Motivação

**Problema:**
Skills como StaticAnalyzer e FrontendTestExpert precisam executar linters, analisadores de complexidade e ferramentas de cobertura — operações que exigem acesso ao shell do sistema.

**Risco:**
Executar comandos arbitrários pode ser perigoso (deleção de arquivos, exfiltração de dados, instalação de malware).

**Solução:**
Uma tool com 3 camadas de segurança: whitelist de comandos, padrões proibidos (regex), e sanitização de ambiente.

---

## 3. Camadas de Segurança

### 3.1 Whitelist de Comandos
Apenas comandos explicitamente listados podem ser executados:

| Categoria | Comandos |
|-----------|----------|
| Linters | ruff, pylint, flake8, mypy, eslint, prettier |
| Testes | pytest, npm, npx, yarn, cargo, mvn, gradle, go, dotnet |
| Análise | radon, lizard, bandit, semgrep |
| Cobertura | coverage, nyc |
| Git | git (com subcomandos limitados) |
| Utilitários | cat, find, wc, tree, dir |

### 3.2 Subcomandos Git Permitidos
Git é restrito a operações seguras: `status`, `log`, `diff`, `show`, `branch`, `tag`, `ls-files`, `rev-parse`, `describe`, `shortlog`, `add`, `commit`.

Bloqueados: `push`, `force`, `reset --hard`, `clean`, `rm`.

### 3.3 Padrões Proibidos
Regex que detectam tentativas de injeção:
- Operadores de shell: `; & | \` $`
- Path traversal: `../../..`
- Remoção forçada: `rm -rf`
- Download + exec: `curl|sh`, `wget|sh`
- Invocação de shell: `powershell`, `cmd /c`, `eval`, `exec`

### 3.4 Sanitização de Ambiente
Variáveis sensíveis (tokens, API keys) são removidas do ambiente do subprocesso.

---

## 4. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Validar comando contra whitelist antes de executar. | Must |
| RF-02 | Rejeitar comandos com padrões de injeção. | Must |
| RF-03 | Limitar timeout (padrão 120s, máximo 600s). | Must |
| RF-04 | Truncar output para evitar estouro de contexto (8k chars). | Must |
| RF-05 | Remover variáveis sensíveis do env do subprocesso. | Must |
| RF-06 | Suportar Windows (shell=True) e Linux (subprocess_exec). | Must |
| RF-07 | Logar todas as execuções para auditoria. | Should |

---

## 5. Localização

```
core/tools/shell.py  ← Implementação da tool
```
