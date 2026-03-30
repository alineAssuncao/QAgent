# Spec: Skill — TestDocWriter (Documentação de Testes)

**Versão:** 1.0 | **Status:** Aprovada | **Data:** 2026-03-29

---

## 1. Resumo
O **TestDocWriter** gera documentação profissional de testes: planos de teste (IEEE 829), matrizes de rastreabilidade, cenários BDD (Gherkin), relatórios de risco e glossários técnicos.

## 2. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Gerar plano de testes baseado em IEEE 829 simplificado. | Must |
| RF-02 | Criar matriz de rastreabilidade (requisito ↔ teste). | Must |
| RF-03 | Escrever cenários BDD em formato Gherkin. | Should |
| RF-04 | Gerar relatório de risco com fórmula CC × cobertura. | Should |
| RF-05 | Criar glossário técnico do projeto. | Could |
| RF-06 | Documentar apenas dados reais (nada genérico). | Must |

## 3. Localização
```
agents/skills/TestDocWriter/
└── SKILL.md
```
