# Spec: Agent Loop (Reasoning Engine)

**Versão:** 1.2 (Python Migration)
**Status:** Aprovada
**Autor:** Aline Assunção
**Data:** 2026-03-28

---

## 1. Resumo

O **Agent Loop** é o motor de execução do **QAgent**. Ele implementa o padrão **ReAct** (Reasoning and Acting), onde as mensagens de entrada são submetidas à IA para gerar um pensamento (**Thought**), seguido de uma ação (**Action**) via ferramentas (Tools), observando o resultado (**Observation**) e repetindo até chegar a uma resposta final.

O loop é implementado utilizando **AsyncIO** para garantir que as chamadas às APIs de LLM e a execução de ferramentas locais não bloqueiem o fluxo do bot.

---

## 2. Contexto e Motivação

**Problema:**
Diferente de um chat estático, um Agente Orquestrador de QA precisa agir no ambiente local (criar arquivos, rodar testes) e aprender com os resultados dessas ações.

**Evidências:**
Tentativas de gerar planos de teste complexos em uma única interação costumam falhar por falta de validação intermediária. O Loop permite que o agente valide cada etapa antes de prosseguir.

---

## 3. Goals (Objetivos)

- [ ] G-01: Executar iterações assíncronas agnósticas (suportando Gemini, DeepSeek, etc.).
- [ ] G-02: Integrar com o **ToolRegistry** para executar ferramentas Python locais.
- [ ] G-03: Implementar limite determinístico de iterações (`MAX_ITERATIONS`) para evitar loops infinitos.

---

## 4. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Suportar o registro dinâmico de ferramentas (Tools) baseadas em classes Python. | Must | O Agente consegue invocar métodos de ferramentas registradas. |
| RF-02 | Injetar resultados de ferramentas (`Observation`) no array de mensagens para a próxima iteração. | Must | O contexto da conversa é mantido e evolui conforme as ferramentas agem. |
| RF-03 | Gerar logs detalhados de cada etapa (Thought, Action, Observation) no console. | Must | Visibilidade total do raciocínio em tempo real no terminal. |

---

## 5. Fluxo Principal (Happy Path)

1. Entrada: Chamada do método `AgentLoop.run()`.
2. Compilação do `System Prompt` com as ferramentas disponíveis nas skills ativas.
3. LLM analisa o histórico e decide pela chamada de uma ferramenta (ex: `rodar_pytest`).
4. O `ToolFactory` instancia a ferramenta e executa a ação de forma assíncrona.
5. O resultado (Ex: "3 testes passaram") é injetado como **Observation**.
6. O LLM gera a resposta final: "Todos os testes passaram, aqui está o relatório."

---

## 6. Edge Cases

- **Erro de JSON**: Se a IA gerar um Tool Call inválido, o loop envia um erro para a IA pedindo correção.
- **Timeout**: Se a ferramenta ou a IA demorar excessivamente, o loop interrompe e notifica o usuário.
- **Max Iterations**: Ao atingir o limite (ex: 5 interações), o agente desiste e explica o motivo da interrupção.

---

## 7. Segurança

Todas as ferramentas executadas pelo **QAgent** devem operar em diretórios controlados e sanitizar inputs antes de execuções no sistema de arquivos para evitar injeção de comandos maliciosos.
