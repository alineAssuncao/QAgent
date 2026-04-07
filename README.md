# QAgent - Orquestrador de QA e Automação

O **QAgent** é um agente de Inteligência Artificial especializado na orquestração de testes automatizados e assistência técnica para equipes de QA e Desenvolvimento.

## 🚀 Visão Geral

Operando como um bot do Telegram, o QAgent permite que você gerencie suítes de testes, analise relatórios e execute comandos de automação diretamente do seu dispositivo móvel ou desktop, mantendo toda a execução e dados de forma local e privada.

### 🌐 Portabilidade e Caminhos Dinâmicos
O QAgent foi projetado para ser 100% portátil. Ele utiliza caminhos dinâmicos resolvidos em tempo de execução (via `BASE_DIR`), o que permite que o projeto seja movido para qualquer diretório or operado em diferentes sistemas sem a necessidade de reconfigurar caminhos de banco de dados ou pastas temporárias.

## 🧠 Funcionalidades Avançadas

O QAgent evoluiu de um simples bot de chat para um **Agente Autônomo** com capacidades de decisão:

-   **Engine ReAct (Reasoning and Acting)**: O bot planeja suas ações (Thought), executa ferramentas (Action) e analisa os resultados (Observation) antes de fornecer a resposta final.
-   **Suporte a Repositórios Externos**: Capacidade de clonar qualquer repositório Git público para a pasta `/projects` e realizar análises profundas do código fonte.
-   **Gestão de Fila e Concorrência**: Sistema inteligente que permite enfileirar até 3 tarefas simultâneas, com menus interativos para priorização ou cancelamento.
-   **Workflows Estruturados (QA-First)**:
    1.  **Detecção Automática**: Links Git ativam o fluxo de análise.
    2.  **Planejamento**: O Agente gera um plano de testes e espera a **aprovação do usuário** via botões.
    3.  **Implementação**: Criação automática de testes unitários após aprovação.
    4.  **Relatório Visual V3**: Geração automática de um Dashboard autossuficiente (`qa_coverage_dashboard.html`) com métricas hiper-densas, histórico de tendências e suporte multi-idioma (EN/PT-BR).
    5.  **Finalização**: Opções interativas para **Commit**, **Push** e **Limpeza**.

## 📊 Dashboard Visual (Data-Dense Reporting)

O QAgent gera agora um relatório técnico avançado inspirado em painéis de analytics profissionais:
- **Universal Parser**: O Agente lê a saída bruta do terminal (Stdout) e entende automaticamente o formato dos testes (Pytest, Jest, JUnit).
- **Independente**: O arquivo `.html` gerado na pasta do projeto funciona standalone (não requer servidor para visualização).
- **Persistência de Histórico**: As métricas de execuções passadas são mantidas nos gráficos de linha para análise de evolução de qualidade.
- **Insights por IA**: Observações críticas sobre a arquitetura e riscos detectados durante a suíte de testes.
O QAgent responde a comandos de controle mesmo enquanto está processando uma tarefa pesada:
-   **"cancelar" / "parar"**: Abre o menu de interrupção imediata da tarefa atual.
-   **"fila" / "status"**: Exibe o estado atual da fila de tarefas e permite gerenciá-la.

## 🛠️ Principais Tecnologias

- **Linguagem:** Python 3.11+
- **Bot Framework:** [aiogram](https://docs.aiogram.dev/)
- **IA/LLMs:** Gemini, DeepSeek, e modelos locais via LM Studio e Ollama
- **Processamento de Áudio:** Faster-Whisper (STT) e Edge-TTS (TTS)
- **Banco de Dados:** SQLite (persistência local)

## 📁 Estrutura do Projeto

- `agents/`: Contém a lógica dos agentes e o diretório de `skills/`.
- `core/`: Núcleo do sistema (bot, configuração, engine de raciocínio ReAct, ferramentas).
- `handlers/`: Gerenciadores de entrada (texto, áudio, PDF) e saída (mensagens, áudio, botões).
- `memory/`: Camada de persistência (SQLite) e repositórios de mensagens e tarefas.
- `projects/`: Pasta (ignorada pelo Git) onde são armazenados os repositórios analisados.
- `specs/`: Documentação técnica e especificações arquiteturais.

## ⚙️ Configuração Rápida

1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`. (Requer ambiente com Python >= 3.11).
3. **Módulos de Teste**: Certifique-se de ter o `pytest` e `pytest-cov` instalados para o funcionamento pleno dos runners Python.
4. Configure o arquivo `.env` (veja `.env.example`).
5. Execute o bot: `python main.py`.

## 📄 Documentação

Para mais detalhes sobre a arquitetura e o funcionamento do projeto, consulte a pasta [specs/](QAgent/specs).