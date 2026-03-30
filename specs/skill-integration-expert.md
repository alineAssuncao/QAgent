# Spec: Sub-Skill — IntegrationExpert (Testes de Integração)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** QAgent Team
**Data:** 2026-03-29

---

## 1. Resumo

O **IntegrationExpert** é a sub-skill especializada na criação de testes de integração que validam a interação entre módulos, endpoints internos e conexões com banco de dados. Ocupa a camada intermediária da pirâmide de testes.

---

## 2. Contexto e Motivação

**Problema:**
Testes unitários garantem que funções isoladas funcionam, mas não garantem que os módulos conversam corretamente entre si. Bugs de integração (ex: contrato quebrado entre service e repository) são os mais custosos.

**Solução:**
Um especialista que detecta automaticamente endpoints/services e gera testes de integração com isolamento adequado de dependências externas.

---

## 3. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Detectar framework web do projeto (FastAPI, Flask, Express, Spring, etc.). | Must |
| RF-02 | Mapear dependências entre módulos (controller→service→repository). | Must |
| RF-03 | Gerar testes usando TestClient/supertest adequado ao framework. | Must |
| RF-04 | Criar fixtures de banco in-memory para isolamento. | Must |
| RF-05 | Separar testes de integração em diretório próprio (`tests/integration/`). | Should |
| RF-06 | Suportar markers/tags para execução seletiva. | Should |

---

## 4. Localização

```
agents/skills/QA_Maestro/subskills/IntegrationExpert/
├── SKILL.md
└── references/
    ├── integration_patterns.md
    └── database_testing.md
```
