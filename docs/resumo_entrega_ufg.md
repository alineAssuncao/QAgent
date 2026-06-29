# QAgent: Orquestrador Inteligente de QA e Automação
## Entrega - Disciplina de Agentes Inteligentes (UFG)

### 1. Visão de Negócio e Proposta de Valor
O **QAgent** não é apenas uma ferramenta de automação, mas um **Multiplicador de Força** para equipes de desenvolvimento e QA. Ele resolve um gargalo crítico na engenharia de software moderna: a latência entre o desenvolvimento do código e a validação da sua qualidade.

#### O Problema:
Atualmente, a criação de testes e a manutenção da cobertura são tarefas manuais, lentas e repetitivas, que consomem até 40% do tempo dos desenvolvedores seniores e sobrecarregam os analistas de QA.

#### A Solução (Visão de Negócio):
O QAgent atua como uma **Banca de Especialistas Onipresente**, disponível 24/7, que reduz drasticamente o *Time-to-Market* ao automatizar a geração e execução de testes. 
- **Redução de Custo Operacional**: Automatiza tarefas repetitivas, permitindo que a equipe humana foque em casos de uso complexos e experiência do usuário (UX).
- **Consistência e Qualidade**: Elimina falhas humanas em testes de rotina e garante que nenhum código chegue à produção sem análise arquitetural.
- **Agilidade na Tomada de Decisão**: Através de interfaces acessíveis (Telegram e futuramente Web), gestores podem monitorar a saúde do projeto em tempo real, de qualquer lugar.

#### Diferenciais Estratégicos:
- **Portabilidade Total**: Projetado para ser executado localmente ou em nuvem com zero configuração de caminhos.
- **Otimização de Custo (LLM Fallback)**: Utiliza inteligência de baixo custo (Gemini Free Tier) e alterna para provedores de alta performance apenas quando necessário, garantindo o melhor ROI em IA.
- **Independência de Infraestrutura**: Capaz de clonar e analisar repositórios dinamicamente, sem necessidade de ambientes pré-configurados.

---

### 2. Fundamentos Técnicos (Estado Atual)
O sistema opera como um **Agente Autônomo** coordenado por um modelo de orquestração multi-especialista.

- **Engine ReAct (Reasoning and Acting)**: O diferencial cognitivo do QAgent. Ele não apenas "cospe" código; ele planeja cada etapa (`Thought`), executa ferramentas reais no terminal/sistema (`Action`) e analisa o feedback (`Observation`) para corrigir seus próprios erros antes de entregar o resultado.
- **Arquitetura Multi-Agente**: Operação coordenada entre:
  - **Maestro (Orquestrador)**: O gestor do projeto que quebra objetivos complexos em tarefas atômicas.
  - **Analista de Sistemas**: Mapeia riscos e arquitetura do código.
  - **Coder & Tester**: Agentes focados na implementação e validação técnica rigorosa.
- **Persistência e Checkpointing (SQLite)**: Uso de banco de dados local com modo WAL (Write-Ahead Logging) para garantir a persistência de conversas, fila de tarefas e logs de execução, permitindo a recuperação do estado após interrupções.
- **Omnicanalidade e Acessibilidade**: Integração nativa com Telegram, oferecendo suporte a áudio (STT/TTS) para interações fluidas e rápidas.

---

### 2. Plano de Evolução (Foco da Matéria)
A evolução pretendida visa transformar o QAgent de uma ferramenta utilitária em uma plataforma de governança de QA robusta, com foco em quatro frentes principais:

#### A. Interface Web Centralizada
Migração do paradigma de chat para um **Dashboard Web (Next.js)**. Isso permitirá uma visualização mais densa de informações, facilitando o monitoramento de múltiplos projetos simultaneamente sem as limitações de interface de um bot de mensagens.

#### B. Controle de Acesso e Autenticação
Implementação de uma camada de segurança para garantir que apenas usuários autorizados possam interagir com os agentes. Isso inclui:
- Login e gestão de sessões.
- Diferenciação de papéis (usuário vs. administrador).
- Proteção de dados sensíveis dos repositórios analisados.

#### C. Visualização de Métricas e Dashboards
Transformar os dados brutos de execução em insights acionáveis:
- Gráficos dinâmicos de cobertura de código.
- Histórico de tendências de qualidade (pass/fail).
- Monitoramento em tempo real da fila de tarefas dos agentes.

#### D. Explorador de Testes e Resultados
Uma interface visual para inspeção profunda dos artefatos criados pela IA:
- Visualização dos testes gerados antes/depois da execução.
- Logs detalhados de falhas integrados à interface web.
- Possibilidade de disparar novas rodadas de teste com um clique.

#### E. Evolução da Infraestrutura de Dados
Transição da persistência local para uma arquitetura escalável:
- **Migração para PostgreSQL**: Para suportar alta concorrência e integridade de dados necessária em um ambiente multi-usuário (Web).
- **Integração com Banco de Dados Vetorial (ex: ChromaDB/Pinecone)**: Implementação de "Memória de Longo Prazo" via RAG (Retrieval Augmented Generation). Isso permitirá que os agentes consultem padrões de código e testes de projetos passados, tornando-se mais inteligentes a cada nova execução.

---

### 3. Impacto Esperado
Com essas evoluções, o projeto demonstrará não apenas a aplicação de técnicas avançadas de IA (Agentes, ReAct, Orquestração), mas também a viabilidade de integrar essas tecnologias em um produto de software escalável, seguro e centrado na experiência do usuário (DevEx).
