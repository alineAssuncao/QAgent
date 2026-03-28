# Spec: Memory Module (SQLite Persistence)

**Versão:** 1.2 (Python Migration)
**Status:** Aprovada
**Autor:** Aline Assunção
**Data:** 2026-03-28

---

## 1. Resumo

O módulo de persistência de estado do **QAgent** gerencia as conversas de curto e longo prazo utilizando um banco de dados **SQLite**. Além de persistir as mensagens do Telegram, este módulo atua como um gestor da janela de contexto, realizando o truncamento inteligente das mensagens mais antigas para evitar o estouro do limite de tokens (Context Window) das APIs de LLM.

---

## 2. Contexto e Motivação

**Problema:**
LLMs são *stateless* — eles não se lembram de interações anteriores por conta própria. Para ser um Agente Orquestrador de testes útil, o **QAgent** precisa reter o contexto de sessões passadas para entender a evolução do projeto de automação.

**Evidências:**
Armazenar o histórico apenas em memória RAM do Python resultaria na perda de todo o contexto ao reiniciar o agente. O uso de arquivos JSON ficaria lento com o crescimento dos dados.

---

## 3. Goals (Objetivos)

- [ ] G-01: Prover armazenamento persistente e rápido de mensagens do Telegram em SQLite.
- [ ] G-02: Possuir um `MemoryManager` central (Facade) que decide automaticamente quando as mensagens velhas devem ser truncadas na requisição para a IA.
- [ ] G-03: Utilizar o **Repository Pattern** para desacoplar a lógica de negócio do SQL puro.

---

## 4. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | O Singleton do Banco deve criar as tabelas `conversations` e `messages` se não existirem no startup. | Must | Persistência automática em `data/qagent.db` (resolvido via `BASE_DIR`). |
| RF-02 | O Storage deve usar o modo **WAL (Write-Ahead Logging)** para leituras e escritas assíncronas concorrentes. | Must | Múltiplas mensagens simultâneas da equipe não bloqueiam o banco. |
| RF-03 | A classe abstrata deve repassar ao Agent Loop apenas o número `MEMORY_WINDOW_SIZE` de mensagens recentes. | Must | O Prompt enviado para LLMs como Gemini não falhará por excesso de tokens de histórico. |

---

## 5. Modelo de Dados (SQLite)

### Tabela: `conversations`
*   `id`: UUID string (Primary Key)
*   `user_id`: String (ID Whitelisted do Telegram)
*   `provider`: String (ex: 'gemini', 'deepseek')

### Tabela: `messages`
*   `id`: Integer (Auto-increment Primary Key)
*   `conversation_id`: String (Foreign Key)
*   `role`: String ('user', 'assistant', 'system', 'tool')
*   `content`: String (Payload da mensagem)
*   `timestamp`: Datetime (Padronizado para UTC)

---

## 6. Tecnologia Utilizada
O módulo utilizará a biblioteca nativa **`sqlite3`** do Python ou **`SQLAlchemy`** (Async Engine) para garantir performance e facilidade de manutenção.

---

## 7. Segurança e Privacidade
- **Dados Locais**: O arquivo `.db` reside no hardware da equipe (conforme definido na arquitetura).
- **.gitignore**: O diretório de dados (`data/`) deve ser excluído do versionamento no Git para proteger o histórico das conversas.
