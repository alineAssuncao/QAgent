# Tratamentos e Handlers: A Interface do QAgent

Como o sistema lida com diferentes formas de entrada e saída (Voz, Texto, PDF, HTML) para manter a fluidez do workflow.

---

## 1. Input Context Handling (Percepção)

O QAgent foi projetado para ser **Multi-Modal**. A entrada de dados não se limita a comandos de texto.

### A. Fluxo de Áudio (Faster-Whisper STT)
Quando o usuário envia uma mensagem de voz via Telegram:
1.  O sistema faz o download do arquivo `.ogg`.
2.  Utiliza o modelo local `Faster-Whisper` (executado em CPU com quantização `int8` para performance).
3.  A transcrição é injetada no loop de raciocínio como se fosse um comando textual.
4.  **Benefício**: Permite que o desenvolvedor descreva problemas complexos de lógica sem precisar digitar.

### B. Processamento de Documentação (PDF/Code)
-   **PDF Parser**: Utiliza `fitz (PyMuPDF)` para extrair texto de especificações técnicas enviadas pelo usuário.
-   **Fallback Project**: Se o usuário enviar um arquivo `.py` solto, o sistema automaticamente cria uma estrutura de projeto temporária para permitir a análise e geração de testes unitários.

---

## 2. Output & Feedback (Resposta)

A resposta do agente é adaptativa, visando a melhor experiência de leitura ou audição.

### A. Resposta Vocal (Edge-TTS)
-   Para feedbacks rápidos ou status de sucesso, o agente pode converter mensagens em voz usando `Edge-TTS` (Voz `pt-BR-ThalitaNeural`).
-   O sistema limpa o Markdown (removendo hashtags e asteriscos) antes da síntese para garantir uma locução natural.

### B. Gestão de Chunks (Telegram API)
-   Mensagens longas de log ou código são automaticamente quebradas em blocos de **4096 caracteres**.
-   O sistema garante que botões interativos e menus sejam anexados apenas ao último bloco enviado, mantendo a ergonomia da interface.

---

## 3. Geração de Relatórios Visuais (Dashboard V3)

O "tratamento" mais avançado ocorre na tradução de logs brutos de teste para interfaces ricas.

-   **Universal Parser**: O sistema lê o stdout do terminal e identifica padrões de `Pytest`, `Jest` ou `JUnit`.
-   **HTML Standalone**: Gera um dashboard HTML moderno com:
    -   Gráficos de tendência de cobertura.
    -   Detalhamento de falhas por arquivo.
    -   Insights gerados por IA sobre riscos arquiteturais.
-   **Diferencial**: O Dashboard não precisa de um servidor. Ele é enviado como um arquivo via Telegram e pode ser aberto em qualquer navegador, preservando a privacidade dos dados.

---

## 4. Gestão de Fila e Finitude

Diferente de bots de chat comuns, o QAgent trata cada solicitação como uma **Tarefa de Background**.
-   **Enqueueing**: Comandos pesados entram em uma fila persistente no SQLite.
-   **Checkpointing**: Se ocorrer um erro de conexão ou estouro de cota da API da LLM, o agente entra em estado de pausa e retoma assim que o recurso estiver disponível, sem perder o progresso já realizado.
