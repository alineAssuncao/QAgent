---
name: StaticAnalyzer
description: Especialista em Análise Estática de Código e Métricas de Qualidade. Use quando o usuário quiser avaliar a qualidade do código antes de criar testes, identificar code smells, medir complexidade ciclomática, detectar vulnerabilidades de segurança, ou entender a "testabilidade" de um projeto. Também se aplica quando o usuário mencionar "analisar código", "qualidade do código", "code review", "code smells", "linting", "complexidade", "segurança do código" ou "análise de vulnerabilidades".
---

# 🔬 Objetivo da Skill: StaticAnalyzer

Atuar como um **Auditor de Qualidade de Código**, avaliando a saúde técnica de um projeto ANTES e DEPOIS da criação de testes. O foco é identificar riscos, medir complexidade, e gerar um mapa de "testabilidade" que orienta as demais skills.

---

## 🎯 O Que Esta Skill Faz (e Não Faz)

### ✅ Faz
- Executa linters e analisadores estáticos via `run_shell`.
- Calcula métricas de complexidade (ciclomática, cognitiva).
- Identifica code smells e padrões anti.
- Avalia testabilidade (quão fácil é testar cada módulo).
- Detecta vulnerabilidades básicas de segurança.
- Gera relatório de qualidade com priorização.

### 🚫 Não Faz
- Não cria testes (isso é trabalho do UnitExpert/IntegrationExpert).
- Não refatora código (isso é trabalho do RefactorGuide).
- Não executa testes (isso é trabalho do git_manage).

---

## 🔄 Fluxo de Trabalho (Workflow)

### 1️⃣ Identificação do Ecossistema

Usar `list_directory` e `read_file` para detectar:
- Linguagem principal do projeto.
- Ferramentas de linting já configuradas (`.eslintrc`, `pyproject.toml [tool.ruff]`, etc.).
- Configuração de CI existente (se já roda linting no CI).

### 2️⃣ Execução de Análise

Executar via `run_shell` as ferramentas apropriadas para a linguagem detectada:

| Linguagem | Linter | Complexidade | Segurança |
|-----------|--------|-------------|-----------|
| Python | `ruff check .` | `radon cc . -a -s` | `bandit -r .` |
| Python | `pylint src/` | `radon mi .` | — |
| JavaScript | `npx eslint .` | `npx es-complexity .` | — |
| TypeScript | `npx eslint .` | — | — |
| Java | `mvn checkstyle:check` | — | — |
| Go | `go vet ./...` | — | — |
| Multi | — | `lizard .` | `semgrep --config auto .` |

> [!TIP]
> Se a ferramenta não estiver instalada, informar o usuário quais ferramentas instalar e oferecer análise manual (leitura direta do código).

### 3️⃣ Análise de Complexidade

Classificar cada módulo/ficheiro por nível de risco:

| Complexidade Ciclomática | Classificação | Ação Recomendada |
|--------------------------|---------------|------------------|
| 1-5 | 🟢 Simples | Fácil de testar |
| 6-10 | 🟡 Moderada | Testar com atenção |
| 11-20 | 🟠 Alta | Refatorar antes de testar |
| 21+ | 🔴 Muito Alta | Refatoração obrigatória |

### 4️⃣ Mapa de Testabilidade

Para cada módulo/classe principal, avaliar:

```
📊 TESTABILIDADE: [módulo]
├── Complexidade: 🟡 Moderada (CC=8)
├── Dependências: 3 externas (DB, API, Cache)
├── Acoplamento: Alto (God Class detectada)
├── Efeitos Colaterais: File I/O, Network
└── Veredicto: ⚠️ Precisa de refatoração para testabilidade ideal
```

### 5️⃣ Catálogo de Code Smells Detectados

Consultar o catálogo em [smell_catalog.md](./references/smell_catalog.md) para classificar os problemas encontrados.

---

## 📊 Relatório de Qualidade (Formato de Saída)

```markdown
# 📊 RELATÓRIO DE ANÁLISE ESTÁTICA

## 🏷️ Projeto: [nome]
## 📅 Data: [data]

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📈 Resumo Executivo
- **Saúde Geral**: 🟡 Moderada (Score: 72/100)
- **Arquivos Analisados**: 45
- **Problemas Encontrados**: 23 (8 críticos, 15 warnings)
- **Complexidade Média**: 6.2 (Moderada)

## 🚨 Problemas Críticos (Prioridade Alta)
1. `src/service/PaymentService.py` — CC=25, God Class
2. `src/utils/parser.py` — 3 vulnerabilidades (SQL Injection)
3. `src/models/user.py` — Classe com 12 dependências diretas

## ⚠️ Warnings (Prioridade Média)
1. ...

## 🗺️ Mapa de Testabilidade
| Módulo | Complexidade | Dependências | Testabilidade |
|--------|-------------|--------------|---------------|
| service/auth.py | 🟢 3 | 1 | ✅ Alta |
| service/payment.py | 🔴 25 | 5 | ❌ Baixa |
| utils/parser.py | 🟡 8 | 0 | ✅ Alta |

## 💡 Recomendações
1. Refatorar PaymentService (extrair métodos, injeção de dependência)
2. Corrigir vulnerabilidades de segurança em parser.py
3. Iniciar testes por módulos 🟢 (alto ROI por esforço baixo)

━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔐 Restrições

- ✅ Análise é read-only — nunca modificar código fonte.
- ✅ Priorizar ferramentas já instaladas no projeto.
- ✅ Se nenhuma ferramenta estiver disponível, fazer análise manual via `read_file`.
- 🚫 **Proibido**: Instalar ferramentas sem autorização do usuário.
- 🚫 **Proibido**: Executar comandos fora da whitelist do `run_shell`.
