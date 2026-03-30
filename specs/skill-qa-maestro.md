# Spec: Skill — QA_Maestro (Orquestrador Central)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** QAgent Team
**Data:** 2026-03-29

---

## 1. Resumo

O **QA_Maestro** é a skill orquestradora central do QAgent, responsável por coordenar e delegar tarefas de QA para sub-skills especializadas. Ele atua como um "maestro" que analisa a solicitação do usuário, identifica o tipo de teste necessário, e aciona a sub-skill correta para execução.

---

## 2. Contexto e Motivação

**Problema:**
O QAgent precisa lidar com múltiplos tipos de testes (unitários, integração, API, frontend) sem sobrecarregar o contexto do LLM com todas as instruções simultaneamente.

**Solução:**
Um orquestrador que faz o roteamento inteligente para sub-skills especializadas, carregando apenas as instruções relevantes para cada tipo de tarefa.

---

## 3. Goals (Objetivos)

- [x] G-01: Coordenar o fluxo de clonagem → análise → planejamento → execução de testes.
- [x] G-02: Rotear para `UnitExpert` quando o pedido é de testes unitários.
- [ ] G-03: Rotear para `IntegrationExpert` quando o pedido é de testes de integração.
- [ ] G-04: Rotear para `APITestExpert` quando o pedido é de testes de API.
- [ ] G-05: Rotear para `FrontendTestExpert` quando o pedido é de testes de frontend/UI.

---

## 4. Sub-Skills Gerenciadas

| Sub-Skill | Status | Propósito |
|-----------|--------|-----------|
| UnitExpert | ✅ Ativa | Testes unitários (ISTQB, AAA, FIRST) |
| IntegrationExpert | 🔜 Planejada | Testes de integração entre módulos |
| APITestExpert | 🔜 Planejada | Testes de endpoints REST/GraphQL |
| FrontendTestExpert | 🔜 Planejada | Testes de componentes e E2E |

---

## 5. Fluxo Principal

1. Usuário envia comando com link Git ou referência a projeto local.
2. QA_Maestro clona/identifica o repositório.
3. QA_Maestro analisa a estrutura e detecta frameworks.
4. QA_Maestro identifica qual tipo de teste é necessário.
5. QA_Maestro aciona a sub-skill especializada.
6. Sub-skill gera o plano de testes e aguarda aprovação.
7. Após aprovação, sub-skill implementa e executa os testes.
8. QA_Maestro entrega o relatório final ao usuário.

---

## 6. Regras de Negócio

- **Transparência**: O usuário deve ser informado sobre cada etapa.
- **Aprovação obrigatória**: Nenhum teste é implementado sem aprovação prévia.
- **Caminhos relativos**: Usar sempre `projects/` como base para repositórios.
- **Foco na base**: Priorizar testes unitários quando o tipo não é explicitado.

---

## 7. Localização

```
agents/skills/QA_Maestro/
├── SKILL.md
└── subskills/
    ├── UnitExpert/
    │   ├── SKILL.md
    │   └── references/
    ├── IntegrationExpert/   (planejada)
    ├── APITestExpert/       (planejada)
    └── FrontendTestExpert/  (planejada)
```
