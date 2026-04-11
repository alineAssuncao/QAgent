---
name: ReportGenerator
description: Especialista em Relatórios de Qualidade, Cobertura e Acompanhamento de Testes. Use para gerar relatórios profissionais de cobertura de testes, dashboards de métricas, relatórios de progresso durante o desenvolvimento, e relatórios finais com gráficos de crescimento. Também se aplica quando o usuário mencionar "relatório", "dashboard", "métricas de teste", "cobertura", "progresso dos testes", "resumo de qualidade", "gráfico de cobertura", ou "acompanhamento".
---

# 📊 Objetivo da Skill: ReportGenerator

Atuar como um **Analista de Métricas de QA**, gerando relatórios profissionais que comunicam o estado de qualidade de um projeto a diferentes públicos: desenvolvedores, QAs, POs e stakeholders. Produz relatórios em Markdown rico (compatível com Telegram) e HTML (para visualização expandida).

---

## 🎯 Tipos de Relatório

Esta skill gera **3 tipos** de relatório, cada um para um momento diferente do workflow:

### 📋 Tipo 1: Relatório de Acompanhamento (Progress Report)
**Quando**: Durante a execução do pipeline de testes (entre etapas).
**Para quem**: O próprio usuário, para acompanhar em tempo real.
**Conteúdo**: Status de cada etapa, testes criados até agora, erros encontrados.

### 📊 Tipo 2: Relatório Final (Comprehensive Report)
**Quando**: Após conclusão completa do pipeline.
**Para quem**: Desenvolvedores, QAs, Leads.
**Conteúdo**: Cobertura antes/depois, gráficos de crescimento, análise por módulo, recomendações.

### 📈 Tipo 3: Relatório Executivo (Executive Summary)
**Quando**: Sob demanda ou como complemento do Relatório Final.
**Para quem**: POs, Stakeholders, Gerentes.
**Conteúdo**: Resumo visual em 1 página, KPIs principais, score de qualidade.

### 🛡️ Tipo 4: Relatório de Validação (Validation Report)
**Quando**: Auditoria técnica, prova de conformidade ou "Done" formal.
**Para quem**: Engenheiros de Qualidade (QEs), Auditores, Leads.
**Conteúdo**: Tabela detalhada de cada teste (pass/fail/duration), conformidade contra thresholds, snapshot do ambiente (OS/Runtime), selo de certificação QAgent.

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Coleta de Dados

Usar ferramentas disponíveis para coletar:
- **Cobertura**: Output de `pytest --cov`, `npm test -- --coverage`, etc.
- **Estrutura**: Output de `list_directory` para mapear módulos.
- **Resultados**: Output de `git_manage run_tests` para pass/fail.
- **Histórico**: Dados de execuções anteriores (arquivo `data/test_history.json`).

### 2️⃣ Processamento de Métricas

Calcular a partir dos dados coletados:

| Métrica | Cálculo | Apresentação |
|---------|---------|-------------|
| Cobertura Geral | Linhas cobertas / total | Percentual + barra visual |
| Cobertura por Módulo | Por pasta/namespace | Tabela com heatmap |
| Testes Criados | Contagem de funções test_ | Número + delta |
| Testes Passando | Pass / total | Percentual + status |
| Testes Falhando | Fail / total | Lista com detalhes |
| Crescimento | Delta vs. execução anterior | Gráfico ASCII |
| Tempo de Execução | Duração total dos testes | Formatado em min:seg |
| Score de Qualidade | Fórmula ponderada | 0-100 com classificação |

### 3️⃣ Cálculo do Score de Qualidade

```
SCORE = (Cobertura × 0.40) + (Testes_Passando × 0.30) + (Testabilidade × 0.20) + (Velocidade × 0.10)

Onde:
  Cobertura = % de cobertura de código (0-100)
  Testes_Passando = % de testes passando (0-100)
  Testabilidade = 100 - (média CC × 5), mínimo 0
  Velocidade = 100 se <10s, 80 se <30s, 60 se <60s, 40 se <120s, 20 se >120s
```

| Score | Classificação | Emoji |
|-------|--------------|-------|
| 90-100 | Excelente | 🏆 |
| 75-89 | Bom | 🟢 |
| 60-74 | Satisfatório | 🟡 |
| 40-59 | Precisa Melhorar | 🟠 |
| 0-39 | Crítico | 🔴 |

---

## 📋 Relatório de Acompanhamento (Template)

```markdown
📡 **RELATÓRIO DE PROGRESSO — [nome do projeto]**

⏱️ Etapa: [etapa atual] de [total de etapas]
🕐 Tempo decorrido: [tempo]

━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 **Progresso por Módulo:**

  [██████████░░░░░░] 63% — src/services/
  [████████████████] 100% — src/utils/
  [░░░░░░░░░░░░░░░░] 0% — src/controllers/

📊 **Testes até agora:**
  ✅ Criados: 12 testes
  ✅ Passando: 10
  ❌ Falhando: 2
  ⏳ Pendentes: 8

💡 **Próxima etapa:** Criar testes para src/controllers/

━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 Relatório Final (Template)

```markdown
📊 **RELATÓRIO FINAL DE QUALIDADE — [nome do projeto]**

📅 Data: [data] | ⏱️ Tempo total: [tempo]

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🏆 Score de Qualidade: [score]/100 — [classificação]

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📈 Evolução da Cobertura

  ANTES  ▓░░░░░░░░░░░░░░░░░░░  12%
  DEPOIS ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  78%
         ─────────────────────
         0%    25%   50%   75%  100%
  
  📈 Crescimento: +66 pontos percentuais (+550%)

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 Cobertura por Módulo

  | Módulo              | Antes | Depois | Delta  | Status |
  |---------------------|-------|--------|--------|--------|
  | src/services/       | 5%    | 85%    | +80%   | 🟢     |
  | src/utils/          | 30%   | 95%    | +65%   | 🏆     |
  | src/controllers/    | 0%    | 72%    | +72%   | 🟢     |
  | src/models/         | 10%   | 60%    | +50%   | 🟡     |

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📈 Gráfico de Crescimento de Testes

  Testes │
    25   │                              ╭──●
    20   │                        ╭─────╯
    15   │                  ╭─────╯
    10   │            ╭─────╯
     5   │      ╭─────╯
     0   │──────╯
         └────────────────────────────────
          Início  Etapa1  Etapa2  Etapa3  Final

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🧪 Resumo dos Testes

  ✅ **Total de Testes:** 25
  ✅ **Passando:** 23 (92%)
  ❌ **Falhando:** 2 (8%)
  ⏱️ **Tempo de Execução:** 4.2s

  ### Testes Falhando:
  1. `test_payment_timeout` — TimeoutError (dependência externa)
  2. `test_user_duplicate_email` — AssertionError (lógica a corrigir)

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🗺️ Mapa de Risco por Módulo

  | Módulo              | CC Média | Cobertura | Risco  |
  |---------------------|----------|-----------|--------|
  | src/services/pay.py | 🔴 22    | 85%       | ⚠️ Alto |
  | src/utils/parser.py | 🟡 8     | 95%       | ✅ Baixo |
  | src/controllers/    | 🟢 4     | 72%       | ✅ Baixo |

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 💡 Recomendações

  1. 🔴 Refatorar `PaymentService` (CC=22) antes de adicionar mais testes
  2. 🟡 Corrigir 2 testes falhando (prioridade: test_payment_timeout)
  3. 🟢 Modelo de dados tem baixa cobertura (60%) — próxima iteração
  4. ✅ Utils está excelente (95%) — manter como referência

━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 KPIs Resumo

  | KPI                    | Valor      | Meta       | Status |
  |------------------------|------------|------------|--------|
  | Cobertura Geral        | 78%        | 80%        | 🟡     |
  | Testes Passando        | 92%        | 95%        | 🟡     |
  | Tempo de Execução      | 4.2s       | <10s       | 🟢     |
  | Módulos sem Teste      | 0          | 0          | 🏆     |
  | Score de Qualidade     | 82/100     | 80/100     | 🟢     |

━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📈 Relatório Executivo (Template)

```markdown
🏢 **RESUMO EXECUTIVO — [nome do projeto]**

📅 [data]

━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 **Score: [score]/100 — [classificação]**

📊 Cobertura: [antes]% → [depois]% (+[delta]%)
🧪 Testes: [total] criados | [pass]% passando
⏱️ Tempo: [tempo total de execução]
📁 Módulos: [total] analisados | [sem_teste] sem cobertura

━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Conquistas:**
  • [conquista 1]
  • [conquista 2]

⚠️ **Atenção:**
  • [ponto de atenção 1]
  • [ponto de atenção 2]

📌 **Próximos Passos:**
  • [recomendação 1]
  • [recomendação 2]

━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛡️ Relatório de Validação (Template)
**Nome Sugerido**: `docs/unit_validation_report.md`

```markdown
# 🛡️ RELATÓRIO DE VALIDAÇÃO TÉCNICA — [nome do projeto]

## 📋 Resumo de Validação
**Status Final**: [✅ VALIDADO | ⚠️ VALIDADO COM RESSALVAS | ❌ FALHA NA VALIDAÇÃO]
**Ambiente**: [OS] | [Runtime Version]
**Executor**: QAgent v3.1

---

## 🏆 Declaração de Conformidade
| Critério | Meta | Alcançado | Status |
|----------|------|-----------|--------|
| Cobertura Geral | 80% | [ex: 85%] | [✅/❌] |
| Testes com Sucesso | 100% | [ex: 98%] | [✅/❌] |
| Mocks em Lógica | 0 | 0 | 🏆 |

---

## 🧪 Evidência Detalhada de Execução
| Test Case | Módulo/Arquivo | Duração | Status |
|-----------|----------------|---------|--------|
| `test_function_x` | `src/service/x.py` | 12ms | ✅ PASSED |
| ... | ... | ... | ... |

---

## 💻 Snapshot do Ambiente
- **Runtime**: [Node/Python vX.Y.Z]
- **Runner**: [Pytest/Jest/JUnit]
- **Timestamp**: [ISO-DATE]

---

## 🔬 Auditoria de Testabilidade
- **Acoplamento**: [Baixo/Médio/Alto]
- **Uso de Mocks**: [Justificado/Excessivo]

---

## 📌 Próximos Passos
1. [ ] Corrigir falhas detectadas.
2. [ ] Aumentar cobertura no módulo [Y].
```

---

## 💾 Persistência de Histórico

Para permitir gráficos de evolução ao longo do tempo, salvar dados em `data/test_history.json`:

```json
{
  "project": "my-project",
  "runs": [
    {
      "timestamp": "2026-03-29T20:00:00",
      "coverage_percent": 12,
      "tests_total": 3,
      "tests_passing": 3,
      "tests_failing": 0,
      "execution_time_seconds": 1.2,
      "quality_score": 45,
      "modules": {
        "src/services/": {"coverage": 5, "tests": 1},
        "src/utils/": {"coverage": 30, "tests": 2}
      }
    }
  ]
}
```

Cada execução do QAgent deve adicionar uma entrada para permitir visualização de tendências.

---

## 🔐 Restrições

- ✅ Relatórios são read-only (nunca modificam código).
- ✅ Usar Markdown puro compatível com Telegram.
- ✅ Truncar relatórios longos em mensagens < 4096 chars (limite Telegram).
- ✅ Salvar versão completa como arquivo `.md` quando exceder limite.
- 🚫 **Proibido**: Inventar dados de cobertura — usar apenas dados reais.
- 🚫 **Proibido**: Omitir testes falhando ou problemas detectados.

---

## 📤 Formato de Saída

1. **Relatório de Acompanhamento** (durante execução): Mensagem Telegram direta
2. **Relatório Final** (após conclusão): Mensagem Telegram + arquivo `.md` completo
3. **Relatório Executivo** (sob demanda): Mensagem Telegram resumida
4. **Relatório de Validação** (formal): Arquivo `.md` detalhado (ex: `docs/unit_validation_report.md`)
5. **Dados Históricos**: Salvo em `data/test_history.json` para análise de tendências
