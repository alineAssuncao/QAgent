# 🚀 Relatório de Melhorias Arquiteturais e Estabilização - QAgent

Este documento consolida as principais refatorações e melhorias implementadas no projeto **QAgent**, visando transformar a ferramenta de um orquestrador instável para um **pipeline de automação robusto, determinístico e visualmente rastreável**.

---

## 1. 🏗️ Orquestração Híbrida: Substituição do ReAct por Execução Determinística

Anteriormente, o sistema utilizava fluxos **ReAct (Reasoning and Acting)** com Inteligência Artificial para descobrir arquivos e executar comandos finais. Isso causava alucinações ("estou executando as ferramentas" sem de fato chamar código) ou loops infinitos de análise.

* **Analista Determinístico:** Criamos a função `_descobrir_arquivos_para_teste` em `controller.py`. Em vez de usar um LLM, o QAgent agora varre fisicamente o sistema de arquivos via Python para descobrir candidatos de módulos Python que requerem testes.
* **Tester via Subprocess (`pytest`):** Eliminamos a persona do LLM que inspecionava se os testes passaram. Agora, instanciamos nativamente o `pytest` garantindo extrações precisas e não enviesadas de sucesso ou falha, com limite `maxfail=5`.
* **Coder Limitado:** O Coder (única persona ainda no ReAct puro) foi limitado nativamente a **10 iterações**, suficientes para (1) ler o código, (2) escrever o teste inicial e (3) realizar no máximo uma ou correções se necessário, cortando loops infinitos decorrentes de códigos difíceis.

## 2. 🛡️ Resiliência no Core, Parsing de Respostas e Fallbacks

A variação de respostas era responsável por bugs de *parsing* e falhas na invocação de Ferramentas (Tools).

* **JSON Parser de Fallback em ReAct:** Se um modelo "esquecer" o formato padrão estruturado do framework (`Action:`) e devolver puramente o JSON da tool, o `loop.py` consegue decodificar.
* **Priorização OpenAI e Tratamento de Quedas:** Garantimos a chamada à **OpenAI (`gpt-4o-mini`)** de forma primária (com maior estabilidade sintática).
* **Gestão do "Erro 429":** Modelos Google Gemini caem em esquema de saúde/fallback. Se batermos a quota, a aplicação migra para provedores vizinhos sem abortar.

## 3. 📂 Isolamento Total da API e Diretórios Python (`--rootdir`)

Uma das maiores dores detectadas: os testes não eram validados, enganando todo o pipeline da aplicação final.

* **Isolamento de Contexto (`pytest` Sandbox):** O pacote do `pytest` chamado para testar os repositórios (como `python-simple-rest-api`) estava lendo, erroneamente, o `pytest.ini` da raiz do projeto mãe (`QAgent`). Ao injetarmos explícito `f"--rootdir={project_abs}"` (e `--override-ini`), engaiolamos as verificações no projeto a ser analisado garantindo que a suíte saiba onde procurar os testes e os arquivos fonte originais da API a ser testada.

## 4. 📊 Dashboard, Tratamento de Métricas e Relatórios

Havia um bug silenciado em que falhas prematuras cancelavam a emissão da métrica de cobertura.

* **Integração Plena (Tests Failed):** Em caso de falhas de importação ou execução em série abortando o pytest, agora resgatamos a métrica através do JSON Breakdown para popular o log e avisamos no Telegram de forma muito clara os Testes Passaram/Falharam em vez de uma mensagem de erro genérica de falha em código ('Metrics Parsing fail').
* **Mensageria Dashboard/CLI:** As mesmas labels (`⚠️ Atenção: X testes falharam...`) são dinamicamente exibidas tanto no CLI local e Terminal, quanto injetadas no Markdown Final e incorporadas no Dashboard Insights, tornando totalmente rastreável o esforço gerado durante o processamento de código.

## 5. 🖇️ Sync Dinâmico (Checklists no Pipeline)

Havia confusão metodológica na entrega do relatório ao longo do tempo. Separamos os comportamentos:

* **`test_plan_qagent.md` (Checklist Tático Contínuo):** É sobrescrito iterativamente usando os registros via banco SQLite. Serve como *To-Do log* dos arquivos descobertos. Marca exatamente `[V]` ou `[X]` a cada subtask de teste realizada para total apoio em possíveis travamentos.
* **`relatorio_testes_qagent.md` (Sumário Consolidado Final):** Exibido perfeitamente apenas quando o Telegram entra em fase final (dashboard success), com links e um espelho idêntico da mensagem do Telegram, finalizando por completo o output com visual limpo.

## 6. 🌟 Refatoração para Arquitetura Multi-Agente

A evolução mais marcante da nova versão foi sair de um modelo de Prompt "monolítico" (faz tudo de uma vez) para um ecossistema **Multi-Agente Especializado** com divisão e delegação transparente de tarefas.

* **Especialização por Papel (Persona):** Segmentamos o esforço em times artificiais delimitados. Temos definições claras do "Analista" (Discovery), o "Coder" (Cria a lógica e escreve os `.py`), o "Tester" (Roda comandos rigorosos de avaliação cruzada e validação de código) e até criadores super focados no output web como o `VisualDashboardGenerator`.
* **Separação de Contexto (Context Window Limpa):** Como cada agente herda seu próprio contexto, eles podem iterar e chamar as Ferramentas (Tools) da máquina apenas focados na sua atribuição exata, reduzindo severamente vazamentos de alucinações (como um tester gerar UI ou o analista codar algo na raiz sem querer).

---

## 7. 🪲 Estabilidade Extrema e Proteção de Sistema (Windows e APIs)

Implementamos uma camada defensiva de isolamento e compatibilidade local, prevenindo travamentos globais originados de execuções incorretas de testes.

* **Tratamento de Encoding (`UnicodeDecodeError`):** Adicionamos uma política de fallback na decodificação de subprocessos no pacote de controle Git (`errors='replace'`) ao tentar ler streams STDERR e STDOUT nativas do Windows. Isso previne que caracteres especiais travem a leitura dos testes gerados.
* **Circuit-Breaker de Comandos Base (`Timeout`):** A execução de processos de shell e validação do sistema agora engloba uma barreira assíncrona mandatória de exclusão de processos (*timeout de 120s*). Isso impede que testes bloqueantes acidentalmente gerados pela IA (como requisições `HTTPServer` rodando indefinidamente) congelem todo o cérebro do bot.
* **Patch em Vazamento de I/O do Windows:** Silenciamos avisos excessivos (`ValueError: I/O operation on closed pipe`) atrelados ao fechamento súbito do Event Loop (protocolo Proactor) base no Windows, limpando a saída no terminal.
* **Prevenção de Spam na Interface Telegram:** Interceptamos preventivamente advertências limiares da API do Telegram (`Message is not modified`), mantendo os cards de progresso ao vivo fixos sem forçar o recarregamento na tela (spam) do usuário em etapas repetitivas de inferência.
