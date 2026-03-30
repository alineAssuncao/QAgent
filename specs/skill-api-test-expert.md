# Spec: Sub-Skill — APITestExpert (Testes de API)

**Versão:** 1.0 | **Status:** Aprovada | **Data:** 2026-03-29

---

## 1. Resumo
O **APITestExpert** gera testes para endpoints REST/GraphQL com cobertura de happy path, validação, autenticação e erros. Detecta rotas automaticamente e valida contratos.

## 2. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Detectar endpoints automaticamente (decorators/routers). | Must |
| RF-02 | Gerar cenários em 4 categorias (happy, validation, auth, error). | Must |
| RF-03 | Criar fixtures de autenticação (token factory). | Must |
| RF-04 | Validar schemas de response (Pydantic, JSON Schema). | Should |
| RF-05 | Separar testes em `tests/api/`. | Should |
| RF-06 | Gerar relatório de cobertura de endpoints. | Should |

## 3. Localização
```
agents/skills/QA_Maestro/subskills/APITestExpert/
├── SKILL.md
└── references/
    └── http_status_guide.md
```
