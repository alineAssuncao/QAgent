# Spec: Skill Management System (Hot-Reload)

**Versão:** 1.2 (Python Migration)
**Status:** Aprovada
**Autor:** Aline Assunção
**Data:** 2026-03-28

---

## 1. Resumo

A arquitetura de injeção de habilidades (**Skills**) possibilita que novas capacidades QA/Dev e guias complexos se integrem dinamicamente ao **QAgent** sem necessidade de reinicialização. Através deste sistema (Loader -> Router -> Executor), cada subpasta vira uma funcionalidade especializada reconhecida pelo LLM.

---

## 2. Contexto e Motivação

**Problema:**
Adicionar inteligência em nível de código dificulta a manutenção e aumenta o acoplamento do sistema. Alterar um prompt ou uma diretriz de teste não deve exigir um novo deploy do bot.

**Evidências:**
Se o LLM receber todas as diretrizes de QA (Unit, Back, Front, Regressivo) simultaneamente, ele sofre de perda de atenção e estouro da janela de contexto. A injeção dinâmica de skill selecionada otimiza o processamento.

---

## 3. Goals (Objetivos)

- [ ] G-01: Mapear o diretório local `agents/skills` em busca de arquivos `SKILL.md`.
- [ ] G-02: Executar o **SkillRouter** (LLM leve) para decidir qual habilidade carregar com base na intenção do usuário.
- [ ] G-03: Inserir a documentação profunda da Skill selecionada no **Master Context** do loop atual (Runtime Injection).

---

## 4. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | **SkillLoader**: Abrir síncrono ou assíncrono o diretório de skills (resolvido via `SKILLS_DIR` dinâmico) e extrair o YAML Frontmatter (`name`, `description`). | Must | Disponibiliza um dicionário de metadados das skills instaladas. |
| RF-02 | **SkillRouter**: Prompt forçado que retorna apenas um JSON: `{"skillName": "xyz" | null}`. | Must | Fallback automático para conversa casual se nenhuma skill for mapeada. |
| RF-03 | **SkillExecutor**: Injetar o conteúdo Markdown da skill selecionada no `System Role` do ReAct Loop. | Must | O Agente assume a persona e as ferramentas da skill em runtime. |

---

## 5. Fluxo Principal (Happy Path)

1. **Entrada**: "Analise este código e gere um Plano de Testes".
2. **Loader**: Identifica localmente as pastas `QA_Maestro` e `UnitExpert`.
3. **Router**: Dispara chamada leve enviando apenas os resumos (Ex: "UnitExpert: Analisa e gera testes unitários").
4. **Decisão**: Router retorna `{"skillName": "UnitExpert"}`.
5. **Execução**: O conteúdo de `UnitExpert/SKILL.md` (instruções ISTQB, AAA, FIRST) e suas ferramentas são injetados no loop ReAct.
6. **Resposta**: O QAgent responde com o Plano de Testes formatado conforme as diretrizes da skill.

---

## 6. Tecnologia Utilizada
O carregamento de arquivos será realizado utilizando a biblioteca nativa **`pathlib`** do Python para garantir portabilidade entre SOs (Windows/Linux). O parse do Frontmatter utilizará a biblioteca **`PyYAML`** ou regex nativo.

---

## 7. Melhores Práticas de Skill
- **Portabilidade**: As skills devem usar caminhos relativos para suas referências internas.
- **Isolamento**: Cada skill deve possuir seu próprio diretório e ser independente das demais.
- **Hot-Reload**: A leitura do disco ocorre a cada nova requisição, garantindo que mudanças no `SKILL.md` reflitam instantaneamente no comportamento do **QAgent**.
