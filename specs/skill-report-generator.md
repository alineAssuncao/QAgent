# Spec: Skill — ReportGenerator (Relatórios de QA)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** QAgent Team
**Data:** 2026-03-29

---

## 1. Resumo

O **ReportGenerator** é a skill de relatórios do QAgent. Gera relatórios profissionais de acompanhamento (progresso), relatórios finais com gráficos de crescimento de cobertura, e resumos executivos. Persiste histórico para análise de tendências.

---

## 2. Contexto e Motivação

**Problema:**
O output bruto de ferramentas de teste (pytest, jest) é técnico e difícil de interpretar para stakeholders. Além disso, não há visibilidade de progresso durante execuções longas.

**Solução:**
Um gerador de relatórios que transforma dados brutos em dashboards visuais (ASCII art para Telegram) com métricas claras, gráficos de evolução e recomendações acionáveis.

---

## 3. Tipos de Relatório

| Tipo | Momento | Público | Conteúdo Principal |
|------|---------|---------|-------------------|
| Acompanhamento | Durante execução | Usuário/Dev | Progresso por módulo, testes criados |
| Final | Após conclusão | Dev/QA/Lead | Cobertura antes/depois, gráficos, KPIs |
| Executivo | Sob demanda | PO/Stakeholder | Score de qualidade, 1 página, KPIs |

---

## 4. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Gerar relatório de acompanhamento com barras de progresso ASCII. | Must |
| RF-02 | Gerar relatório final com cobertura antes/depois e delta. | Must |
| RF-03 | Incluir gráfico de crescimento de testes (ASCII art). | Must |
| RF-04 | Calcular Score de Qualidade (0-100) com fórmula ponderada. | Must |
| RF-05 | Gerar mapa de risco por módulo (complexidade × cobertura). | Should |
| RF-06 | Persistir histórico em `data/test_history.json`. | Must |
| RF-07 | Gerar relatório executivo resumido (1 página). | Should |
| RF-08 | Respeitar limite de 4096 chars do Telegram (truncar + enviar .md). | Must |
| RF-09 | Incluir tabela de KPIs com metas e status. | Should |
| RF-10 | Listar testes falhando com detalhes de erro. | Must |

---

## 5. Fórmula do Score de Qualidade

```
SCORE = (Cobertura × 0.40) + (Testes_Passando × 0.30) + (Testabilidade × 0.20) + (Velocidade × 0.10)
```

---

## 6. Localização

```
agents/skills/ReportGenerator/
├── SKILL.md
└── references/
    └── report_templates.md
```
