# Spec: Telegram Output Handler

**Versão:** 1.2 (Python Migration)
**Status:** Aprovada
**Autor:** Aline Assunção
**Data:** 2026-03-28

---

## 1. Resumo

O módulo de **Output** do **QAgent** é a interface final de resposta do agente. Ele capta o resultado processado pelo **Agent Loop** ou pelas **Skills** e define a estratégia de exibição adequada:
1. **Fracionamento** de mensagens de texto longas (> 4096 caracteres).
2. **Envio de arquivos** Markdown ou relatórios complexos.
3. **Sintetização de voz** (TTS) para respostas rápidas.

---

## 2. Contexto e Motivação

**Problema:**
APIs de LLM geram respostas longas que ultrapassam o limite do Telegram. O envio direto falha com erros de payload. Além disso, documentações técnicas extensas (como Planos de Teste) são melhor consumidas como arquivos para download.

**Evidências:**
Uma equipe de QA gera relatórios de centenas de linhas que o Telegram não suporta em uma única bolha de chat.

---

## 3. Goals (Objetivos)

- [ ] G-01: Prover a interface `TelegramOutputHandler` para separar a lógica de envio do bot principal.
- [ ] G-02: Fragmentar automaticamente textos que excedam 4096 caracteres.
- [ ] G-03: Encapsular arquivos gerados (Ex: `reports.md`) e enviar como anexo via Telegram.
- [ ] G-04: Gerar áudio (`.ogg`) via **Edge-TTS** caso o usuário requisite ou o input tenha sido em voz.

---

## 4. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | **Text Splitter**: Dividir strings longas sem quebrar palavras ou blocos de código. | Must | Respostas extensas chegam em múltiplos balões de chat cronológicos. |
| RF-02 | **File Attach**: Interceptar flags de arquivo e enviar via `reply_document` do **aiogram**. | Must | Arquivos `.md` ou `.json` gerados são enviados como anexo. |
| RF-03 | **TTS (Saída de Voz)**: Converter texto em voz utilizando a biblioteca **edge-tts** em Python. | Must | Respostas enviadas via nota de voz (`reply_voice`). |
| RF-04 | **Error Feedback**: Formatar erros críticos em blocos visuais (Ex: ⚠️). | Must | Transparência em caso de falhas de IA ou execução. |

---

## 5. Estratégias de Saída (Patterns)

### A. TextOutputStrategy
Fragmentação inteligente utilizando o método `split_text` para garantir que o Telegram aceite o payload sem erros.

### B. FileOutputStrategy
Salva o conteúdo em um arquivo temporário no diretório `TMP_DIR` (resolvido dinamicamente via `BASE_DIR`) e realiza o upload para o Telegram Client do usuário. O arquivo é deletado após o envio.

### C. AudioOutputStrategy
Utiliza a engine **edge-tts** para gerar áudio com vozes de alta qualidade (Ex: `pt-BR-ThalitaNeural`). O arquivo resultante é enviado como mensagem de voz nativa.

---

## 6. Tecnologia Utilizada
- **aiogram**: Métodos assíncronos de envio (`send_message`, `send_document`, `send_voice`).
- **edge-tts**: Biblioteca Python para síntese de voz.
- **Asyncio**: Controle de concorrência e filas de envio.

---

## 7. Edge Cases e Tratamento de Erros

- **Rate Limit (429)**: O bot deve respeitar o tempo de espera (`Retry-After`) retornado pelo Telegram se muitas mensagens forem enviadas sequencialmente.
- **Falha de Escrita**: Se não for possível criar arquivos temporários, o sistema faz o fallback para texto puro no canal de chat.
- **Bloqueio de Bot**: Captura de exceções caso o usuário bloqueie o bot, evitando a queda do processo principal.
