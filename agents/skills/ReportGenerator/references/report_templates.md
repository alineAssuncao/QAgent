# Templates de Relatório — Referência Rápida

## Barras de Progresso ASCII

### Barra Simples (16 chars)
```
[████████████████] 100%
[████████████░░░░]  75%
[████████░░░░░░░░]  50%
[████░░░░░░░░░░░░]  25%
[░░░░░░░░░░░░░░░░]   0%
```

Cálculo: `blocos_cheios = round(percentual / 100 * 16)`
Chars: `█` (cheio) e `░` (vazio)

### Barra Comparativa (Antes vs Depois)
```
ANTES  ▓░░░░░░░░░░░░░░░░░░░  12%
DEPOIS ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  78%
       ─────────────────────
       0%    25%   50%   75%  100%
```

---

## Gráficos ASCII

### Gráfico de Linha (Crescimento)
```
  100% │                              ●
   80% │                        ╭─────╯
   60% │                  ╭─────╯
   40% │            ╭─────╯
   20% │      ╭─────╯
    0% │──────╯
       └────────────────────────────────
        v1.0   v1.1   v1.2   v1.3  v1.4
```

### Gráfico de Barras (Cobertura por Módulo)
```
  services   ████████████████████  95%
  utils      ██████████████████░░  88%
  controllers████████████████░░░░  78%
  models     ████████████░░░░░░░░  60%
  config     ██████░░░░░░░░░░░░░░  30%
```

### Heatmap de Risco (Tabela)
```
  | Módulo        | CC  | Cob  | Risco |
  |---------------|-----|------|-------|
  | payments.py   | 🔴22| 85%  | ⚠️    |
  | auth.py       | 🟡 8| 70%  | ⚠️    |
  | utils.py      | 🟢 3| 95%  | ✅    |
  | models.py     | 🟢 2| 60%  | 🟡    |
```

---

## Emojis Padrão

| Contexto | Emoji | Uso |
|----------|-------|-----|
| Sucesso | ✅ | Testes passando, metas atingidas |
| Falha | ❌ | Testes falhando, erros |
| Aviso | ⚠️ | Pontos de atenção |
| Excelente | 🏆 | Score > 90, cobertura > 95% |
| Bom | 🟢 | Score 75-89, cobertura 75-94% |
| Satisfatório | 🟡 | Score 60-74, cobertura 50-74% |
| Precisa Melhorar | 🟠 | Score 40-59, cobertura 25-49% |
| Crítico | 🔴 | Score < 40, cobertura < 25% |
| Tempo | ⏱️ | Duração de execução |
| Progresso | 📈 | Crescimento, evolução |
| Relatório | 📊 | Métricas, dados |
| Módulo | 📦 | Componentes do projeto |
| Recomendação | 💡 | Sugestões de melhoria |
| Próxima Etapa | 📌 | Ações futuras |

---

## Limites do Telegram

| Tipo | Limite | Ação |
|------|--------|------|
| Mensagem de texto | 4096 chars | Truncar + enviar arquivo .md |
| Caption de arquivo | 1024 chars | Resumo curto |
| Markdown suportado | Subset | Usar MarkdownV2 do Telegram |

### Formatação Telegram (MarkdownV2)
```
*negrito*
_itálico_
`código inline`
```código em bloco```
||spoiler||
```

> [!TIP]
> Para relatórios longos: enviar um resumo como mensagem + arquivo .md completo como documento.

---

## Estrutura de Dados para Histórico

### test_history.json
```json
{
  "project": "project-name",
  "runs": [
    {
      "timestamp": "ISO-8601",
      "run_type": "unit|integration|full",
      "coverage_percent": 0-100,
      "tests_total": int,
      "tests_passing": int,
      "tests_failing": int,
      "tests_skipped": int,
      "execution_time_seconds": float,
      "quality_score": 0-100,
      "modules": {
        "module/path/": {
          "coverage": 0-100,
          "tests": int,
          "complexity_avg": float
        }
      },
      "tools_used": ["pytest", "ruff"],
      "triggered_by": "user|ci|scheduled"
    }
  ]
}
```
