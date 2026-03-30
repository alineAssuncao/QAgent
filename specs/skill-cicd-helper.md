# Spec: Skill — CICDHelper (Assistente CI/CD)

**Versão:** 1.0 | **Status:** Aprovada | **Data:** 2026-03-29

---

## 1. Resumo
O **CICDHelper** gera pipelines de CI/CD para GitHub Actions, GitLab CI e Azure Pipelines, configurados com a suíte de testes criada pelo QAgent.

## 2. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF-01 | Detectar plataforma de Git (GitHub, GitLab, Azure). | Must |
| RF-02 | Gerar pipeline YAML com etapas lint → test → coverage. | Must |
| RF-03 | Suportar matrix de versões (Python 3.10-3.12, Node 18-22). | Should |
| RF-04 | Gerar badges de status/cobertura para README. | Should |
| RF-05 | Não incluir secrets hardcoded no pipeline. | Must |
| RF-06 | Apresentar pipeline para aprovação antes de criar. | Must |

## 3. Localização
```
agents/skills/CICDHelper/
└── SKILL.md
```
