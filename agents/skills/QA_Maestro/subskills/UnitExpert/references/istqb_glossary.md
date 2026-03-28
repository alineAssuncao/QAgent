# 📚 Glossário ISTQB e Shift-Left para UnitExpert

Este guia contém as definições fundamentais baseadas nos currículos **ISTQB CTFL (Certified Tester Foundation Level)** e **CTAL-ATT (Advanced Technical Test Analyst)**.

---

## 🏗️ Nível de Teste: Teste de Componente (Unit Testing)
O **Teste de Componente** (ou teste unitário) foca em componentes que são testáveis de forma isolada. O objetivo é reduzir riscos, verificar comportamentos específicos e prevenir falhas de propagação.

## ⚪ Técnicas de Caixa-Branca (White-Box Testing)
Técnicas baseadas na análise da estrutura interna do componente.

- **Cobertura de Instrução (Statement Coverage)**: Mede a porcentagem de instruções executáveis que foram testadas.
- **Cobertura de Decisão/Ramo (Decision/Branch Coverage)**: Mede a porcentagem de resultados de decisões (True/False) que foram exercitados. 
    *   *Nota*: Alcançar 100% de cobertura de decisão garante 100% de cobertura de instrução, mas o inverso não é verdadeiro.

---

## 🛠️ Isolamento: Test Doubles (Dobrês de Teste)
Objetos que substituem dependências reais durante a execução do teste.

1.  **Stub**: Fornece respostas predefinidas para chamadas feitas durante o teste. Usado para controlar o fluxo de dados de entrada.
2.  **Mock**: Registra as chamadas recebidas para verificar se a interação ocorreu como esperado (parâmetros, ordem, frequência).
3.  **Fake**: Possui uma implementação funcional real, mas simplificada (ex: um banco de dados em memória).
4.  **Dummy**: Objetos passados apenas para preencher parâmetros de funções, mas nunca são usados.
5.  **Spy**: Stubs que também registram informações sobre as chamadas recebidas (semelhante ao mock, mas com foco persistente no estado).

---

## 🚀 Shift-Left Testing
Abordagem que move as atividades de teste para as fases iniciais do ciclo de desenvolvimento. No contexto da **UnitExpert**, isso significa testar o código assim que ele é escrito, antes de qualquer integração ou implantação.

---

## 📏 Critérios de Qualidade (AAA e FIRST)

### Arrange-Act-Assert (AAA)
- **Arrange (Preparar)**: Configurar o estado inicial do teste e dependências.
- **Act (Agir)**: Executar a unidade de código sob teste.
- **Assert (Verificar)**: Validar se o resultado ou comportamento foi o esperado.

### Princípios FIRST
- **Fast (Rápido)**: Testes unitários devem executar em milissegundos.
- **Independent (Independente)**: Um teste não deve depender do resultado de outro.
- **Repeatable (Repetível)**: Deve produzir o mesmo resultado em qualquer ambiente.
- **Self-Validating (Autoavaliável)**: O teste deve ter um resultado binário (Passa/Falha) claro.
- **Timely (Oportuno)**: Escrito idealmente junto com o código de produção (TDD) ou logo após.
