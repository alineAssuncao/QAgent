# Métricas de Qualidade de Código — Guia de Referência

## Complexidade Ciclomática (CC)

**O que é**: Número de caminhos linearmente independentes no código. Cada `if`, `elif`, `for`, `while`, `catch`, `case`, `and`, `or` incrementa a CC.

**Como calcular (Python)**:
```bash
# Instalar: pip install radon
radon cc src/ -a -s          # Mostra CC por função/método
radon cc src/ -a -s -n C     # Apenas CC >= C (alta)
```

**Interpretação**:
| CC | Risco | Testabilidade | Ação |
|----|-------|---------------|------|
| 1-5 | Baixo | Fácil | ✅ Testar normalmente |
| 6-10 | Moderado | Média | ⚠️ Testar com cuidado |
| 11-20 | Alto | Difícil | 🔶 Considerar refatorar |
| 21-50 | Muito Alto | Muito Difícil | 🔴 Refatorar antes |
| 51+ | Inaceitável | Impossível | 🔴 Reescrever |

---

## Índice de Manutenibilidade (MI)

**O que é**: Score de 0-100 que combina CC, volume de Halstead e LOC.

**Como calcular (Python)**:
```bash
radon mi src/ -s     # Mostra MI por arquivo (A-F)
```

**Interpretação**:
| MI | Grade | Significado |
|----|-------|-------------|
| 100-20 | A | Muito manutenível |
| 19-10 | B | Moderadamente manutenível |
| 9-0 | C | Difícil de manter |

---

## Complexidade Cognitiva

**O que é**: Versão moderna da CC que mede "dificuldade cognitiva para entender o código". Penaliza aninhamento profundo.

**Diferença para CC**:
- CC trata `if/else` como 1 ponto.
- Cognitiva penaliza aninhamento: `if` dentro de `if` = 2 pontos, `if` dentro de `if` dentro de `for` = 3 pontos.

---

## Métricas de Dependência

### Fan-In (Acoplamento Aferente)
Quantos módulos dependem DESTE módulo.
- Alto fan-in = módulo crítico (mudanças afetam muitos).

### Fan-Out (Acoplamento Eferente)
De quantos módulos ESTE módulo depende.
- Alto fan-out = módulo complexo (muitas dependências para mockar).

### Instabilidade (I)
`I = Fan-Out / (Fan-In + Fan-Out)`
- I=0: Totalmente estável (muitos dependem dele).
- I=1: Totalmente instável (depende de muitos).

---

## Métricas de Volume

| Métrica | Descrição | Limiar de Alerta |
|---------|-----------|-----------------|
| LOC | Linhas de código por arquivo | > 300 linhas |
| Funções/arquivo | Número de funções por arquivo | > 20 funções |
| Parâmetros/função | Número de parâmetros | > 5 parâmetros |
| Profundidade de aninhamento | Nível máximo de indentação | > 4 níveis |
| Linhas por função | LOC por função/método | > 50 linhas |

---

## Ferramentas por Linguagem

### Python
| Ferramenta | Instalar | Comando | O que mede |
|------------|----------|---------|------------|
| ruff | `pip install ruff` | `ruff check .` | Linting rápido |
| pylint | `pip install pylint` | `pylint src/` | Linting completo |
| radon | `pip install radon` | `radon cc . -a -s` | Complexidade |
| bandit | `pip install bandit` | `bandit -r .` | Segurança |
| mypy | `pip install mypy` | `mypy src/` | Tipos |

### JavaScript / TypeScript
| Ferramenta | Instalar | Comando | O que mede |
|------------|----------|---------|------------|
| eslint | `npm i -D eslint` | `npx eslint .` | Linting |
| prettier | `npm i -D prettier` | `npx prettier --check .` | Formatação |

### Multi-linguagem
| Ferramenta | Instalar | Comando | O que mede |
|------------|----------|---------|------------|
| lizard | `pip install lizard` | `lizard .` | Complexidade multi-lang |
| semgrep | `pip install semgrep` | `semgrep --config auto .` | Segurança/padrões |
