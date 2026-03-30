# Spec: Skill — RefactorGuide (Refatoração para Testabilidade)

**Versão:** 1.0 | **Status:** Aprovada | **Data:** 2026-03-29

---

## 1. Resumo
O **RefactorGuide** identifica barreiras de design que impedem a criação de testes eficientes e propõe refatorações seguras e incrementais. Foco em DI, Extract Method/Class, e remoção de estado global.

## 2. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Diagnosticar testabilidade via checklist. | Must |
| RF-02 | Classificar problemas por severidade (crítico→baixo). | Must |
| RF-03 | Gerar plano de refatoração com riscos e impacto. | Must |
| RF-04 | Executar refatorações uma por vez com checkpoint. | Must |
| RF-05 | Verificar testes existentes antes/depois de cada mudança. | Must |
| RF-06 | Atualizar mapa de testabilidade pós-refatoração. | Should |

## 3. Localização
```
agents/skills/RefactorGuide/
├── SKILL.md
└── references/
    └── refactoring_catalog.md
```
