---
name: VisualDashboardGenerator
description: Age como Universal Parser lendo os outputs de Stdout do Test Runner e transforma em JSON estruturado, consolidando o Histórico e ejetando o V3 Visual Dashboard.
---

# Agent Skill: Gerador de Dashboard Visual Estático (Visual Dashboard Generator)

## 🎯 OBJETIVO
Atuar como Universal Parser autônomo. Você converterá os logs brutos (Terminal Stdout)4. **Fallback & Resiliência:** 
   - Se o log estiver vazio ou não houver métricas, NÃO crie um dashboard vazio de erro amigável se possível, mas se precisar escrever, no campo `insights` da estrutura JSON, adicione um item: "Nenhum teste detectado no log de execução." 
5. **Manutenção do Histórico (CRÍTICO):**
   - Antes de sobrescrever o `qa_coverage_dashboard.html`, tente LER o conteúdo atual para extrair o array `history_trend` do JSON `__QA_DATA__` existente. 
   - Se encontrar dados anteriores, ANEXE a nova rodada aos arrays (labels, cov_after, etc.) em vez de reiniciá-los.HTML (Data-Dense Adwords Style). Desta forma, teremos uma página local robusta embarcada na pasta do projeto-alvo (`projects/`).

## 📥 ENTRADAS ESPERADAS
O prompt final fornecerá a você (Normalmente via Controller do QAgent):
- Logs da execução do Test Runner ANTES.
- Logs da execução do Test Runner DEPOIS.
- Coverage inicial e final de sistema.
- Tempo total de processamento.

## 🛠️ COMPORTAMENTO (Agent-Parser)
1. **Atue como Parser:** Leia minuciosamente os textos do Terminal do Pytest/Jest passados no prompt. Extraia cobertura por módulo (breakdown), testes totais (executados, passed, failed, errors) de ambos os turnos.
2. Calcule deltas numéricos lógicos (ex: Before 10%, After 85% = Delta 75%).
3. Gere e escreva os "Insights" cruciais em inglês e pt-br sobre o que o terminal acusou.

## 📚 PERSISTÊNCIA E HISTÓRICO (Estritamente Injetado)
Você precisa alimentar os gráficos de *Trend Analysis* dual-axis.
1. Se for rodar a análise, use a Tool `read_file` no arquivo existente local (ex: `projects/{repositorio}/qa_coverage_dashboard.html`).
2. Se existir, recupere dos dados o Bloco JSON de `history_trend`, extraia todos os arrays antigos e faça um `append` do teste do ciclo atual no final do array.
3. Se não existir, inicie os arrays APENAS com a execução atual.
4. **Gravação Dupla:** Sempre solte um log puro num arquivo paralelo `projects/{repositorio}/qagent_metrics_log.json` contendo estritamente esse mesmo objeto `__QA_DATA__` antes de regerar o HTML, para atuarmos como backup.

## 🔒 RESTRIÇÕES ESTritas (Data-Driven Report)
- NUNCA crie marcações frontend de cabeça. O V3 tem milhares de regras CSS específicas. **OBRIGATORIAMENTE** Utilize a Tool `read_file` em `assets/qa_dashboard_template.html` se for a primeira vez.
- Injete o JSON exatamente entre as tags validas instanciadas por `const __QA_DATA__ =`.
- NUNCA crie ou salve o script na diretriz raiz do QAgent. Use `projects/<projeto>/`.

## 🗃️ FORMATO ESTRUTURADO DE DADOS (JSON Model)
Você deve compor rigorosamente este JSON (note as separações em i18n em "insights"):
```json
{
  "metadata": {
    "run_id": "string",
    "timestamp": "iso-date",
    "branch": "string (opcional)"
  },
  "coverage": {
    "before": 0.00,
    "after": 0.00,
    "delta_absolute": 0.00,
    "delta_percentual": 0.00
  },
  "tests": {
    "total_created": 0,
    "total_executed": 0,
    "failures": 0
  },
  "performance": {
    "generation_time_seconds": 0.0,
    "execution_time_seconds": 0.0
  },
  "breakdown": [
    {
      "module": "filename",
      "coverage_before": 0.0,
      "coverage_after": 0.0,
      "delta": 0.0
    }
  ],
  "insights": {
    "en": ["insight 1"],
    "pt": ["insight 1 pt-br"]
  },
  "history_trend": {
    "labels": ["Day X"],
    "cov_before": [40],
    "cov_after": [80],
    "tests_exec": [100],
    "tests_fail": [0],
    "gen_time": [10],
    "exec_time": [4]
  }
}
```

## 🪄 PROCESSO DE FINALIZAÇÃO DA SKILL
1. Consolide os dados localmente no pensamento construindo validamente.
2. Grave o `.json` puro em `projects/.../qagent_metrics_log.json`.
3. Incorpore no arquivo master `assets/qa_dashboard_template.html`.
4. Salve com overwrite o resultado final em `projects/.../qa_coverage_dashboard.html`.
5. Você deve devolver FINAL_ANSWER anunciando a página pronta.
