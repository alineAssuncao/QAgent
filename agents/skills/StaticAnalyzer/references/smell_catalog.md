# Catálogo de Code Smells

## Classificação de Severidade

| Severidade | Impacto na Testabilidade | Ação |
|------------|--------------------------|------|
| 🔴 Crítico | Bloqueia criação de testes | Refatorar antes de testar |
| 🟠 Alto | Dificulta significativamente | Refatorar se possível |
| 🟡 Médio | Aumenta complexidade dos testes | Testar com cuidado |
| 🟢 Baixo | Impacto menor | Melhorar gradualmente |

---

## Smells de Design

### God Class (🔴 Crítico)
**O que é**: Classe com responsabilidades demais (>300 LOC, >20 métodos, >5 dependências).
**Por que é ruim para testes**: Muitos cenários, muitos mocks, setup extenso.
**Solução**: Extract Class, Single Responsibility Principle.

### Feature Envy (🟠 Alto)
**O que é**: Método que usa mais dados de outra classe do que da própria.
**Por que é ruim para testes**: Acoplamento desnecessário, mais mocks.
**Solução**: Move Method para a classe correta.

### Long Method (🟠 Alto)
**O que é**: Método com >50 linhas ou CC>10.
**Por que é ruim para testes**: Muitos branches, difícil atingir cobertura total.
**Solução**: Extract Method, decomposição funcional.

### Shotgun Surgery (🟡 Médio)
**O que é**: Mudança em um ponto exige mudanças em muitos lugares.
**Por que é ruim para testes**: Testes espalhados, frágeis a mudanças.
**Solução**: Centralizar lógica, Apply Move Method.

---

## Smells de Código

### Dead Code (🟡 Médio)
**O que é**: Código que nunca é executado (imports não usados, funções órfãs).
**Impacto**: Polui análise de cobertura, confunde métricas.
**Detecção**: `ruff check --select F401,F841`, `pylint --disable=all --enable=W0611,W0612`.

### Magic Numbers/Strings (🟡 Médio)
**O que é**: Valores literais sem explicação (`if status == 3`, `timeout = 30000`).
**Impacto**: Testes com valores sem contexto.
**Solução**: Extrair constantes nomeadas.

### Primitive Obsession (🟡 Médio)
**O que é**: Usar tipos primitivos (string, int) em vez de objetos de domínio.
**Impacto**: Testes não validam regras de negócio.
**Solução**: Value Objects, tipos específicos de domínio.

### Duplicated Code (🟡 Médio)
**O que é**: Blocos de código repetidos em 2+ locais.
**Impacto**: Testes duplicados ou cobertura inconsistente.
**Detecção**: `ruff check --select E501`, análise visual.

---

## Smells de Dependência

### Dependency Injection Ausente (🔴 Crítico)
**O que é**: Classes que instanciam suas próprias dependências (`self.db = Database()`).
**Por que é ruim para testes**: Impossível injetar mocks.
**Solução**: Injeção via construtor.

### Acoplamento Temporal (🟠 Alto)
**O que é**: Métodos que devem ser chamados em ordem específica (`init()` antes de `process()`).
**Por que é ruim para testes**: Testes frágeis, setup complexo.
**Solução**: Garantir estado válido via construtor.

### Hidden Dependencies (🔴 Crítico)
**O que é**: Dependências acessadas via global state, singletons ou variáveis de módulo.
**Por que é ruim para testes**: Impossível isolar.
**Solução**: Tornar dependências explícitas via parâmetros.

---

## Smells de Teste (quando testes já existem)

### Teste Frágil (🟠 Alto)
**O que é**: Teste que falha com mudanças insignificantes no código.
**Causa**: Assert muito específico, mock muito restritivo.

### Teste Lento (🟡 Médio)
**O que é**: Teste unitário que demora >1s.
**Causa**: Acesso real a DB, rede, file I/O.

### Test Double Excessivo (🟡 Médio)
**O que é**: Teste com >3 mocks/stubs.
**Causa**: Classe sob teste tem dependências demais.
