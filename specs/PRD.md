# Spec: PRD — QAgent Core

**Versão:** 1.2 (Python Migration)
**Status:** Aprovada
**Autor:** Aline Assunção
**Data:** 2026-03-28
**Reviewers:** Equipe de QA / Desenvolvedores

---

## 1. Resumo

O **QAgent** é um agente de Inteligência Artificial para orquestração de testes automatizados e assistência técnica, operando 100% localmente no desktop do usuário. Ele recebe comandos pelo Telegram, processa-os através de um pipeline que suporta múltiplos LLMs dinamicamente, e utiliza o ecossistema Python para interagir com ferramentas de qualidade e desenvolvimento.

---

## 2. Contexto e Motivação

**Problema:**
Agentes hospedados na nuvem exigem exposição de dados sensíveis e possuem custos altos. No contexto de **QA e Desenvolvimento**, a falta de integração nativa com frameworks de teste locais (como Pytest ou Playwright) limita a utilidade de assistentes genéricos.

**Evidências:**
A necessidade de um orquestrador que não apenas responda perguntas, mas que consiga **gerar, executar e analisar testes automatizados** no próprio ambiente de desenvolvimento do usuário.

**Por que agora:**
A maturidade de LLMs (Gemini, DeepSeek) combinada com a robustez do Python para automação permite criar um "copiloto" de QA que opera via Telegram de forma privada e eficiente.

---

## 3. Goals (Objetivos)

- [ ] G-01: Operar via Telegram utilizando a biblioteca **aiogram** (Python).
- [ ] G-02: Intercambiar "cérebros" (LLMs) usando provedores como LM Studio, Ollama, Gemini e DeepSeek.
- [ ] G-03: Reter contexto em SQLite utilizando o módulo nativo `sqlite3` do Python.
- [ ] G-04: Orquestrar e disparar skills de teste (UnitExpert, BackendExpert, etc.).
- [ ] G-05: Garantir segurança através de Whitelist estrita por ID de usuário do Telegram.

**Métricas de sucesso:**
| Métrica | Baseline | Target |
|---------|----------|--------|
| Tempo de resposta do Bot | < 1s | < 500ms (local) |
| Precisão do Skill Router | N/A | > 95% |
| Sucesso na execução de testware | N/A | > 90% |

---

## 4. Non-Goals (Fora do Escopo)

- NG-01: Não terá interface Web (React/Vue/HTML). A interface é unicamente o Telegram.
- NG-02: Não suportará múltiplos usuários além da Whitelist estrita.
- NG-03: Não utilizará bancos de dados complexos que exijam instalação externa (PostgreSQL/Mongo).

---

## 5. Usuários e Personas

**Usuário Autorizado:** QAs, Desenvolvedores, POs e Team Leads que precisam de auxílio rápido no ciclo de testes via dispositivos móveis ou desktop (Telegram).

**Jornada Futura:**
O usuário solicita a criação ou execução de uma suíte de testes pelo Telegram, enviando a URL de git, path local ou fazendo upload de um **arquivo .py** avulso diretamente; o **QAgent** (rodando localmente) identifica a skill necessária, gera os scripts, executa no host e retorna o relatório de pass/fail diretamente no chat.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Rodar via loop assíncrono utilizando **aiogram**. | Must | O sistema responde a mensagens via Telegram em tempo real. |
| RF-02 | Validar Whitelist contra `TELEGRAM_ALLOWED_USER_IDS`. | Must | Usuários não autorizados são ignorados imediatamente. |
| RF-03 | Alternar Provedores de LLM via `ProviderFactory`. | Must | Configuração simples via `.env` alterna o modelo de IA. |

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Latência de Processamento | < 1000ms | Agilidade na triagem de mensagens. |
| RNF-02 | Linguagem de Implementação | Python 3.11+ | Escolhido pela compatibilidade com ferramentas de QA. |
| RNF-03 | Persistência | SQLite (Built-in) | Simplicidade e portabilidade. |

---

## 8. Design e Interface
Interface baseada exclusivamente em chat do Telegram utilizando Markdown para formatação de relatórios e arquivos para entrega de código de teste.

---

## 9. Modelo de Dados

```sql
conversations {
  id: string        -- UUID da conversa
  user_id: string   -- ID do usuário (Whitelisted)
  provider: string  -- Provedor utilizado (Gemini/DeepSeek)
}
messages {
  id: integer       -- Auto-increment primary key
  conversation_id: string 
  role: string      -- 'user'|'assistant'|'system'|'tool'
  content: string   -- Conteúdo da mensagem
}
```

---

## 10. Integrações e Dependências

| Dependência | Tecnologia | Papel |
|-------------|------------|-------|
| Bot API | **aiogram** | Comunicação com Telegram |
| LLMs | Gemini / DeepSeek | Motor de raciocínio |
| Memória | **sqlite3** | Armazenamento de contexto |
| Multimodalidade | **edge-tts** | Conversão de texto para voz |

---

## 11. Edge Cases e Tratamento de Erros

- **EC-01**: Timeout de API externa -> Notificar usuário e tentar fallback se configurado.
- **EC-02**: Banco de dados corrompido -> Reabertura via journaling ou recriação automática.
- **EC-03**: Arquivo de Skill malformado -> Ignorar carregamento da skill específica sem derrubar o agente.

---

## 12. Segurança e Privacidade
- **Whitelisting**: Proteção total contra acesso não autorizado.
- **Dados Locais**: As conversas e códigos de teste permanecem no hardware do usuário.
