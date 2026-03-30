# Spec: Skill — StaticAnalyzer (Análise Estática)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** QAgent Team
**Data:** 2026-03-29

---

## 1. Resumo

O **StaticAnalyzer** avalia a qualidade do código antes e depois da criação de testes. Executa linters, mede complexidade ciclomática, identifica code smells e gera um mapa de testabilidade que orienta as demais skills.

---

## 2. Contexto e Motivação

**Problema:**
Criar testes para código de alta complexidade sem refatorar primeiro resulta em testes frágeis e de baixo valor.

**Solução:**
Análise prévia que identifica "onde testar primeiro" (alto ROI) e "onde refatorar antes de testar" (alta complexidade).

---

## 3. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Executar linters via `run_shell` com whitelist. | Must |
| RF-02 | Calcular complexidade ciclomática por função/método. | Must |
| RF-03 | Gerar mapa de testabilidade (complexidade × dependências). | Must |
| RF-04 | Identificar code smells via catálogo (smell_catalog.md). | Should |
| RF-05 | Detectar vulnerabilidades básicas de segurança. | Should |
| RF-06 | Gerar relatório de qualidade formatado em Markdown. | Must |

---

## 4. Dependências

- **RunShellTool** (`core/tools/shell.py`): Necessária para executar linters e analisadores.

---

## 5. Localização

```
agents/skills/StaticAnalyzer/
├── SKILL.md
└── references/
    ├── metrics_guide.md
    └── smell_catalog.md
```
