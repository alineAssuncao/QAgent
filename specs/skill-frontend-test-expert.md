# Spec: Sub-Skill — FrontendTestExpert (Testes de Frontend)

**Versão:** 1.0 | **Status:** Aprovada | **Data:** 2026-03-29

---

## 1. Resumo
O **FrontendTestExpert** gera testes de componentes (React, Vue, Angular) usando Testing Library e testes E2E com Playwright.

## 2. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Detectar framework frontend (React, Vue, Angular, Svelte). | Must |
| RF-02 | Gerar testes de componente com Testing Library. | Must |
| RF-03 | Usar queries por prioridade (getByRole > getByLabelText > getByTestId). | Must |
| RF-04 | Gerar scripts E2E Playwright para fluxos críticos. | Should |
| RF-05 | Configurar jest.config/vitest.config/playwright.config. | Should |
| RF-06 | Testar comportamento, não implementação. | Must |

## 3. Dependências
- **RunShellTool** para `npm test`, `npx playwright test`.
- Node.js instalado no ambiente.

## 4. Localização
```
agents/skills/QA_Maestro/subskills/FrontendTestExpert/
└── SKILL.md
```
