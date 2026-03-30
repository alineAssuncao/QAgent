# Spec: Telegram Input Handler

**Versão:** 1.2 (Python Migration)
**Status:** Aprovada
**Autor:** Aline Assunção
**Data:** 2026-03-28

---

## 1. Resumo

O módulo **Telegram Input** captura eventos das APIs do Telegram através da biblioteca **aiogram** (Python). Ele realiza filtragem de segurança por whitelist de ID, converte anexos (documentos PDF e arquivos de áudio) em texto e injeta na memória do ciclo do agente para processamento pela IA.

---

## 2. Contexto e Motivação

**Problema:**
LLMs nativos consomem apenas texto. Para que o **QAgent** seja um orquestrador eficiente, ele precisa "ouvir" comandos de voz e "ler" documentos técnicos (PDFs, Markdowns) enviados pela equipe via Telegram.

**Evidências:**
Usuários frequentemente alimentam o agente com especificações em PDF ou enviam mensagens de voz para comandos rápidos. O processamento STT (Speech-to-Text) local garante privacidade total.

---

## 3. Goals (Objetivos)

- [ ] G-01: Receber mensagens de texto (`message:text`) e encaminhar ao Pipeline AI.
- [ ] G-02: Receber envios de documentos (`.pdf`, `.md`, `.py`) e extrair o conteúdo textual via **PyMuPDF**, ou copiar scripts locais.
- [ ] G-03: Receber mensagens de voz e áudio, realizando a transcrição via **Whisper Local**.
- [ ] G-04: Notificar o usuário com status em tempo real ("Digitando...", "Analisando documento...").

---

## 4. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | **Whitelist**: Filtrar mensagens contra `TELEGRAM_ALLOWED_USER_IDS`. | Must | Acesso restrito apenas a usuários autorizados. |
| RF-02 | **Parse de Documento/Código**: Extrair texto de PDFs, Markdown e alocar scripts Python. | Must | Conteúdo do arquivo é concatenado ou alocado em isolamento sob projetos. |
| RF-03 | **STT (Voz)**: Transcrever áudios utilizando o modelo **Whisper** local. | Must | O texto transcrito é tratado como se fosse uma mensagem digitada. |
| RF-04 | **Flag de Áudio**: Marcar pedidos que exijam resposta em voz (`requires_audio_reply`). | Must | Se o input for voz, a resposta padrão deve ser em voz (TTS). |

---

## 5. Fluxo Principal (Happy Path)

1. **Entrada**: Usuário envia uma nota de voz no Telegram.
2. **Bot**: Valida Whitelist e sinaliza `typing` ou `record_voice`.
3. **Download**: Baixa o arquivo `.ogg`/`.mp3` temporariamente no diretório `TMP_DIR` (resolvido via `BASE_DIR`).
4. **Transcrição**: O módulo **Whisper** processa o áudio e retorna o texto.
5. **Encaminhamento**: O texto e a flag de áudio são injetados no **Agent Loop** para raciocínio.
6. **Limpeza**: Remove o arquivo temporário do disco imediatamente.

---

## 6. Tecnologia Utilizada
- **aiogram**: Framework de bot assíncrono.
- **PyMuPDF** (`fitz`): Extração de texto de PDFs.
- **Faster-Whisper**: Implementação otimizada do Whisper para transcrição STT local.
- **Aiohttp**: Download assíncrono de arquivos da API do Telegram.

---

## 7. Segurança e Privacidade
- **Transcrições Locais**: O processamento de voz ocorre no hardware do usuário, sem envio de áudio para servidores de terceiros.
- **Sanitização**: Filtragem de caracteres nulos ou maliciosos em inputs de texto para proteger o banco SQLite.
