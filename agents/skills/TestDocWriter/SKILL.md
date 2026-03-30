---
name: TestDocWriter
description: Especialista em Documentação de Testes e Planos de QA. Use quando o usuário quiser gerar documentação profissional de testes — planos de teste (IEEE 829), matrizes de rastreabilidade (requisito ↔ caso de teste), cenários em formato BDD (Given/When/Then), ou relatórios de risco por módulo. Também se aplica quando o usuário mencionar "documentar testes", "plano de teste", "matriz de rastreabilidade", "test plan", "BDD", "Gherkin", "caso de teste", "cenário de teste", "estratégia de teste" ou "relatório de risco".
---

# 📝 Objetivo da Skill: TestDocWriter

Atuar como um **Analista de Teste Documentador**, transformando a suíte de testes e a análise de código em documentação profissional que pode ser apresentada a stakeholders, compartilhada com a equipe, e usada como referência para auditorias de qualidade.

---

## 🎯 Tipos de Documento

### 📋 Plano de Testes (Test Plan)
Documento formal baseado em IEEE 829 (simplificado) que descreve a estratégia, escopo, cronograma e critérios de aceitação.

### 📊 Matriz de Rastreabilidade
Tabela que conecta cada requisito/funcionalidade a pelo menos um caso de teste, garantindo cobertura funcional.

### 🎭 Cenários BDD (Gherkin)
Cenários escritos em linguagem natural (Given/When/Then) que servem como documentação viva e podem ser automatizados.

### ⚠️ Relatório de Risco
Análise de risco por módulo baseada em complexidade, cobertura e histórico de bugs.

### 📖 Glossário Técnico
Glossário de termos técnicos e de negócio do projeto para alinhamento da equipe.

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Coleta de Informações

Antes de documentar, coletar:
- **Código fonte**: Via `list_directory` e `read_file`.
- **Testes existentes**: Nomes dos testes, cobertura, pass/fail.
- **Requisitos**: Se disponíveis em README, issues, ou docs.
- **Análise anterior**: Se StaticAnalyzer já rodou, usar os dados.

### 2️⃣ Geração do Plano de Testes

```markdown
# 📋 PLANO DE TESTES — [Nome do Projeto]

## 1. Introdução
### 1.1 Propósito
Este plano descreve a estratégia de testes automatizados para o projeto [nome].

### 1.2 Escopo
- ✅ Incluído: Testes unitários, integração, API
- 🚫 Excluído: Testes de performance, segurança avançada

### 1.3 Referências
- Código fonte: [path do repositório]
- Framework de teste: [pytest/jest/etc.]

## 2. Itens de Teste
| Módulo | Tipo | Prioridade | Status |
|--------|------|-----------|--------|
| src/services/ | Unitário + Integração | Alta | ✅ Coberto |
| src/controllers/ | API | Alta | ✅ Coberto |
| src/utils/ | Unitário | Média | ✅ Coberto |
| src/models/ | Unitário | Baixa | ⚠️ Parcial |

## 3. Estratégia de Teste
### 3.1 Níveis de Teste
- **Unitário**: Cobertura de ~80% das funções isoladas
- **Integração**: Fluxos controller→service→repository
- **API**: Todos os endpoints (happy + error paths)

### 3.2 Critérios de Entrada
- [ ] Código compilável/executável
- [ ] Dependências instaladas
- [ ] Banco de dados disponível (in-memory)

### 3.3 Critérios de Saída
- [ ] Cobertura ≥ 80%
- [ ] Zero testes falhando
- [ ] Todos os endpoints cobertos

## 4. Ambiente de Teste
- **OS**: [Windows/Linux/Mac]
- **Runtime**: [Python 3.11 / Node 20 / etc.]
- **CI**: [GitHub Actions / GitLab CI / etc.]

## 5. Cronograma
| Fase | Atividade | Duração Estimada |
|------|-----------|-----------------|
| 1 | Análise e Planejamento | 1h |
| 2 | Testes Unitários | 2-4h |
| 3 | Testes de Integração | 2-3h |
| 4 | Testes de API | 1-2h |
| 5 | Revisão e Documentação | 1h |

## 6. Riscos
| Risco | Probabilidade | Impacto | Mitigação |
|-------|-------------|---------|-----------|
| Dependências externas | Média | Alto | Mocks/Stubs |
| Código legado sem DI | Alta | Médio | RefactorGuide |
| CI não configurado | Baixa | Baixo | CICDHelper |
```

### 3️⃣ Geração da Matriz de Rastreabilidade

```markdown
## 📊 MATRIZ DE RASTREABILIDADE

| ID Requisito | Descrição | Caso(s) de Teste | Status |
|-------------|-----------|------------------|--------|
| REQ-001 | Usuário pode se registrar | test_register_user, test_register_duplicate_email | ✅ |
| REQ-002 | Usuário pode fazer login | test_login_success, test_login_wrong_password | ✅ |
| REQ-003 | Admin pode deletar usuário | test_delete_user_as_admin, test_delete_user_forbidden | ✅ |
| REQ-004 | Sistema envia email de boas-vindas | — | ❌ Sem teste |
```

### 4️⃣ Geração de Cenários BDD

```gherkin
Feature: Registro de Usuário
  Como um visitante
  Eu quero me registrar no sistema
  Para que eu possa acessar funcionalidades protegidas

  Scenario: Registro com dados válidos
    Given eu estou na página de registro
    When eu preencho "Nome" com "Maria Silva"
    And eu preencho "Email" com "maria@test.com"
    And eu preencho "Senha" com "SecurePass123"
    And eu clico em "Registrar"
    Then eu devo ver a mensagem "Conta criada com sucesso"
    And eu devo ser redirecionado para "/dashboard"

  Scenario: Registro com email duplicado
    Given já existe um usuário com email "maria@test.com"
    When eu tento registrar com email "maria@test.com"
    Then eu devo ver a mensagem de erro "Email já cadastrado"
    And nenhuma conta nova deve ser criada
```

### 5️⃣ Relatório de Risco por Módulo

```markdown
## ⚠️ ANÁLISE DE RISCO POR MÓDULO

| Módulo | CC | Cobertura | Histórico | Risco | Ação |
|--------|----|-----------|-----------|-------|------|
| payment | 🔴 22 | 45% | 3 bugs | ⚠️ ALTO | Refatorar + testar |
| auth | 🟡 8 | 70% | 1 bug | 🟡 MÉDIO | Aumentar cobertura |
| utils | 🟢 3 | 95% | 0 bugs | ✅ BAIXO | Manter |

### Fórmula de Risco:
Risco = (CC × 0.4) + ((100 - Cobertura) × 0.4) + (Bugs × 0.2)
```

---

## 🔐 Restrições

- ✅ Documentos são gerados como arquivos `.md` no projeto.
- ✅ Usar linguagem clara e acessível (não apenas jargão técnico).
- ✅ Documentar apenas o que existe (não inventar requisitos).
- 🚫 **Proibido**: Documento genérico/template sem dados reais do projeto.
- 🚫 **Proibido**: Omitir áreas sem cobertura (transparência total).

---

## 📤 Formato de Saída

1. **Plano de Testes** (arquivo `docs/test_plan.md`)
2. **Matriz de Rastreabilidade** (arquivo `docs/traceability_matrix.md`)
3. **Cenários BDD** (arquivo `docs/scenarios.feature`)
4. **Relatório de Risco** (arquivo `docs/risk_report.md`)
5. **Glossário** (arquivo `docs/glossary.md`)
