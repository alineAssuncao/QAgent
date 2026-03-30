# Spec: Sub-Skill — UnitExpert (Testes Unitários)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** QAgent Team
**Data:** 2026-03-29

---

## 1. Resumo

O **UnitExpert** é a sub-skill especializada em criação, análise e melhoria de testes unitários. Segue os padrões ISTQB (CTFL, CTAL-ATT) com foco em Shift-Left, alta cobertura de decisão e uso consciente de mocks/stubs.

---

## 2. Contexto e Motivação

**Problema:**
A base da pirâmide de testes (testes unitários) é frequentemente negligenciada em projetos reais, resultando em defeitos tardios e custosos.

**Solução:**
Um especialista virtual que detecta linguagem/framework, gera planos de teste e implementa testes unitários de alta qualidade automaticamente.

---

## 3. Goals (Objetivos)

- [x] G-01: Detectar linguagem de programação e sugerir framework de teste adequado.
- [x] G-02: Gerar plano de testes unitários com cenários e estratégia de isolamento.
- [x] G-03: Implementar testes seguindo padrão AAA (Arrange-Act-Assert) e FIRST.
- [x] G-04: Respeitar o gate de aprovação antes de implementação.
- [x] G-05: Gerenciar alterações em testes legados com gate obrigatório.

---

## 4. Requisitos Funcionais

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-01 | Identificar linguagem de programação do repositório. | Must | ✅ |
| RF-02 | Sugerir framework de teste baseado em mapeamento (framework_mapping.md). | Must | ✅ |
| RF-03 | Realizar análise estática básica (complexidade, código morto). | Should | ✅ |
| RF-04 | Medir cobertura de instrução e decisão dos testes existentes. | Must | ✅ |
| RF-05 | Gerar plano de testes com cenários e estratégia de mocks/stubs. | Must | ✅ |
| RF-06 | Implementar testes conforme padrão AAA e FIRST. | Must | ✅ |
| RF-07 | Executar testes e apresentar relatório de cobertura. | Must | ✅ |

---

## 5. Padrões Técnicos

### AAA (Arrange-Act-Assert)
- **Arrange**: Configuração dos dados e mocks necessários.
- **Act**: Execução da unidade sob teste.
- **Assert**: Verificação dos resultados esperados.

### FIRST
- **Fast**: Execução rápida.
- **Independent**: Sem dependência entre testes.
- **Repeatable**: Resultados consistentes.
- **Self-Validating**: Pass/Fail automático.
- **Timely**: Criados junto com o código.

### Isolamento Consciente
- Objetos reais para dependências determinísticas/rápidas.
- Test doubles (Stub, Mock, Fake) apenas para dependências externas ou não-determinísticas.

---

## 6. Referências Bundled

| Arquivo | Propósito |
|---------|-----------|
| `references/framework_mapping.md` | Mapeamento linguagem → framework de teste |
| `references/istqb_glossary.md` | Glossário ISTQB para terminologia padronizada |

---

## 7. Localização

```
agents/skills/QA_Maestro/subskills/UnitExpert/
├── SKILL.md
└── references/
    ├── framework_mapping.md
    └── istqb_glossary.md
```
