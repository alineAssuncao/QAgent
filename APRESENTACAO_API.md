# Roteiro de Apresentação Técnica - QAgent API

**Duração Máxima:** 10 minutos  
**Público-alvo simulado:** Equipe técnica de uma instituição / Stakeholders de TI

---

## 1. Introdução e Contextualização (1 - 2 minutos)
* **Abertura:** Olá, meu nome é Aline. Bem-vindos à apresentação do **QAgent API**.
* **O Problema:** O processo de análise de qualidade e documentação de software muitas vezes é manual e não integrado.
* **A Solução (O que é a API):** O QAgent nasceu como um orquestrador de automação, mas hoje vou apresentar a sua camada de **API REST**. A ideia foi expor a robustez das IAs internas (como LLMs e modelos de áudio) para que qualquer sistema front-end ou mobile da nossa instituição possa consumir serviços de IA de forma padronizada.

## 2. Visão Técnica e Arquitetura (2 minutos)
* **Framework Escolhido:** A API foi desenvolvida em **FastAPI**, escolhido por sua alta performance, suporte assíncrono nativo e documentação automática.
* **Integrações de IA:** A API orquestra **dois serviços principais**:
  1. **Serviço de Chat (LLM):** Utiliza um padrão `ProviderFactory` que permite o plug-and-play de IAs como Gemini, OpenAI ou modelos locais via LM Studio.
  2. **Serviço de Transcrição (Whisper):** Utiliza o `faster-whisper` para rodar STT (Speech-to-Text) 100% local.

## 3. Comprovação dos Requisitos (2 - 3 minutos)
*(Dica: Nesta etapa, exiba a tela do seu editor de código / VSCode e aponte para as linhas relevantes).*
* **Versionamento:** "Todos os nossos endpoints nascem dentro do prefixo `/v1/`, garantindo evolução segura de contrato no futuro." (Mostre o `APIRouter(prefix="/v1")` no arquivo de rotas).
* **Validação de Dados:** "Para garantir que entradas malformadas não cheguem à lógica de negócios, utilizamos o **Pydantic**." (Mostre a classe `ChatRequest` no arquivo `models.py`).
* **Segurança:** "A API não é pública. Configuramos uma autenticação simples, mas eficaz, usando o cabeçalho `X-API-Key`." (Mostre a função de segurança no `main.py`).
* **Tratamento de Erros e Logs:** "Qualquer falha do modelo de IA ou extensão de arquivo inválida no áudio é tratada, levantando `HTTPException` com status HTTP correto (ex: 400 ou 500). Toda a operação é registrada via sistema de logs."

## 4. Demonstração Funcional na Prática (3 minutos)
*(Dica: Abra o navegador no Swagger UI em `http://127.0.0.1:8000/docs`).*
1. **Teste Negativo de Segurança:**
   - Tente realizar uma chamada em qualquer endpoint *sem* se autenticar.
   - Mostre que a API devolve um erro `403 Forbidden` provando o funcionamento da segurança.
2. **Autorizando o Sistema:**
   - Clique no botão "Authorize", insira a sua API Key de teste e clique em autorizar.
3. **Testando o Endpoint `/v1/chat`:**
   - Preencha o Request Body com um JSON enviando uma mensagem simples (ex: "Me explique o que é teste unitário em 2 linhas").
   - Execute e mostre o JSON de retorno com a resposta gerada.
4. **Testando o Endpoint `/v1/transcribe`:**
   - Faça upload de um pequeno arquivo `.ogg` ou `.mp3`.
   - *Nota de atenção para a gravação:* Garanta que o Whisper está configurado corretamente na sua máquina de demonstração e que o ambiente Python possui todas as dependências C++ necessárias compiladas (https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/).
   - Mostre o processamento e a string de texto transcrita retornando.

## 5. Fechamento (1 minuto)
* **Resumo:** A API resolve o problema de fragmentação ao criar um Hub unificado e seguro de IA para a instituição.
* **Próximos Passos:** Menções curtas sobre adoção, métricas, ou uso em produção.
* **Agradecimento:** "Obrigada pelo tempo, fico à disposição da equipe para dúvidas."
