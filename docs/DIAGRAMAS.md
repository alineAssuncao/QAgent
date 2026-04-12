# 🎨 Galeria de Diagramas: QAgent

Esta galeria consolida as visões visuais do projeto, prontas para serem utilizadas em apresentações acadêmicas e documentação técnica.

---

## 1. Visão Conceitual 3D (Slide de Abertura/Solução)

Uma representação artística de alto impacto da "Banca de Especialistas" do QAgent.

![Representação Conceitual QAgent](file:///C:/Users/aline/.gemini/antigravity/brain/36e6f0ac-6af6-4728-bbb5-e4564f51adc7/qagent_architecture_conceptual_3d_1776001475302.png)

---

## 2. Visão de Fluxo de Negócio (Nível Executivo)

Demonstra o valor entregue ao usuário final de forma simples.

```mermaid
graph LR
    A[👤 Usuário/Telegram] -->|Solicita Teste| B(🤖 QA Maestro)
    B -->|Planeja & Delega| C{🧠 Raciocínio ReAct}
    C -->|Executa Ações| D[🛠️ Git/Tools/Files]
    D -->|Gera Resultados| E[🧪 Testes & Cobertura]
    E -->|Consolida| F[📊 Dashboard Visual]
    F -->|Feedback Instantâneo| A
```

---

## 3. Arquitetura Multi-Agente (Nível Técnico)

Detalha a separação de responsabilidades entre os agentes especialistas.

```mermaid
graph TD
    subgraph "Orquestrador"
        M[QA Maestro]
    end

    subgraph "Especialistas (Personas)"
        A[Analista de Software]
        C[Coder Agent]
        T[Tester Agent]
        R[Reporter Agent]
    end

    M -->|Define Tarefas| A
    A -->|Mapeia Código| C
    C -->|Implementa Mocks/Testes| T
    T -->|Valida Execução| R
    R -->|Gera HTML/Markdown| M
```

---

## 4. O Coração do Agente: Ciclo ReAct

O processo iterativo que cada agente segue para garantir o determinismo e evitar alucinações.

```mermaid
stateDiagram-v2
    [*] --> Pensamento
    state "Pensamento (Thought)" as Pensamento
    state "Ação (Action)" as Acao
    state "Observação (Observation)" as Obs
    
    Pensamento --> Acao : Decide qual tool usar
    Acao --> Obs : Executa no ambiente local
    Obs --> Pensamento : Analisa o resultado
    
    Pensamento --> RespFinal : Objetivo alcançado
    RespFinal --> [*]
```

---

## 5. Diagrama de Contexto e Camadas

Visão de sistema completa, do Telegram ao Banco de Dados.

```mermaid
graph TB
    subgraph "Camada de Interface"
        UI[Telegram / Voz / PDF]
    end

    subgraph "Camada de Inteligência"
        CTRL[Dispatcher / Controller]
        LOOP[Motor ReAct]
        LLM[Provedores: Gemini / Local]
    end

    subgraph "Camada de Execução"
        GIT[Gerenciador Git]
        SHELL[Execução Shell Protegida]
        FILES[Manipulação de Arquivos]
    end

    subgraph "Camada de Dados"
        DB[(SQLite - Estado)]
        MD[Markdown - Logs]
    end

    UI <--> CTRL
    CTRL <--> LOOP
    LOOP <--> LLM
    LOOP --> GIT & SHELL & FILES
    FILES --> DB & MD
```
