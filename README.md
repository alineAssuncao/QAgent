# QAgent - Orquestrador de QA e Automação

O **QAgent** é um agente de Inteligência Artificial especializado na orquestração de testes automatizados e assistência técnica para equipes de QA e Desenvolvimento.

## 🚀 Visão Geral

Operando como um bot do Telegram, o QAgent permite que você gerencie suítes de testes, analise relatórios e execute comandos de automação diretamente do seu dispositivo móvel ou desktop, mantendo toda a execução e dados de forma local e privada.

### 🌐 Portabilidade e Caminhos Dinâmicos
O QAgent foi projetado para ser 100% portátil. Ele utiliza caminhos dinâmicos resolvidos em tempo de execução (via `BASE_DIR`), o que permite que o projeto seja movido para qualquer diretório ou operado em diferentes sistemas sem a necessidade de reconfigurar caminhos de banco de dados ou pastas temporárias.

## 🛠️ Principais Tecnologias

- **Linguagem:** Python 3.11+
- **Bot Framework:** [aiogram](https://docs.aiogram.dev/)
- **IA/LLMs:** Gemini, DeepSeek, e modelos locais via LM Studio
- **Processamento de Áudio:** Faster-Whisper (STT) e Edge-TTS (TTS)
- **Banco de Dados:** SQLite (persistência local)

## 📁 Estrutura do Projeto

- `agents/`: Contém a lógica dos agentes e o diretório de `skills/`.
- `core/`: Núcleo do sistema (bot, configuração, engine de raciocínio).
- `handlers/`: Gerenciadores de entrada (texto, áudio, PDF) e saída.
- `memory/`: Camada de persistência e repositórios de mensagens.
- `specs/`: Documentação técnica e especificações arquiteturais.

## ⚙️ Configuração Rápida

1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Configure o arquivo `.env` (veja `.env.example`).
4. Execute o bot: `python main.py` ou use o script `./run.ps1` (no Windows).

## 📄 Documentação

Para mais detalhes sobre a arquitetura e o funcionamento do projeto, consulte a pasta [specs/](QAgent/specs).