---
name: CICDHelper
description: Assistente de CI/CD para automação de testes. Use quando o usuário quiser criar pipelines de CI/CD (GitHub Actions, GitLab CI, Azure Pipelines), configurar execução automática de testes no push/PR, adicionar badges de cobertura ao README, ou integrar o QA workflow com ferramentas de integração contínua. Também se aplica quando o usuário mencionar "pipeline", "CI/CD", "GitHub Actions", "GitLab CI", "Azure Pipelines", "automatizar no CI", "rodar testes no push", "badge de cobertura", ou "deploy".
---

# ⚙️ Objetivo da Skill: CICDHelper

Atuar como um **Engenheiro de CI/CD para QA**, gerando pipelines completos de integração contínua que executam automaticamente a suíte de testes criada pelo QAgent. O foco é garantir que os testes rodem em cada push/PR sem intervenção manual.

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Detecção do Ambiente

Usar `list_directory` e `read_file` para identificar:
- **Plataforma de Git**: GitHub (`.github/`), GitLab (`.gitlab-ci.yml`), Azure DevOps (`azure-pipelines.yml`).
- **Linguagem principal**: Python, Node.js, Java, etc.
- **Framework de teste**: pytest, jest, junit, etc.
- **CI existente**: Se já há pipeline configurado, analisar e melhorar.

### 2️⃣ Geração do Pipeline

Baseado na detecção, gerar o pipeline adequado:

| Plataforma | Arquivo | Localização |
|------------|---------|-------------|
| GitHub Actions | `tests.yml` | `.github/workflows/tests.yml` |
| GitLab CI | `.gitlab-ci.yml` | Raiz do projeto |
| Azure Pipelines | `azure-pipelines.yml` | Raiz do projeto |

### 3️⃣ Estrutura Padrão do Pipeline

Todo pipeline deve incluir estas etapas na ordem:

```
1. 🔍 Lint (Análise Estática)
2. 🧪 Unit Tests (Testes Unitários)
3. 🔗 Integration Tests (Testes de Integração)
4. 📊 Coverage Report (Relatório de Cobertura)
5. 📤 Upload Artifacts (Salvar relatórios)
```

---

## 📋 Templates por Plataforma

### GitHub Actions — Python (pytest)
```yaml
name: QAgent Test Suite
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov ruff
      
      - name: Lint
        run: ruff check .
      
      - name: Unit Tests
        run: pytest tests/unit/ --cov=src --cov-report=xml --cov-report=term
      
      - name: Integration Tests
        run: pytest tests/integration/ -m integration
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

### GitHub Actions — Node.js (jest/vitest)
```yaml
name: QAgent Test Suite
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Tests
        run: npm test -- --coverage
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
```

### GitLab CI — Python
```yaml
stages:
  - lint
  - test
  - coverage

lint:
  stage: lint
  image: python:3.11
  script:
    - pip install ruff
    - ruff check .

unit-tests:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest tests/unit/ --cov=src --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

integration-tests:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest tests/integration/ -m integration
```

---

## 🏷️ Badges de Status

Gerar badges para o README:

### GitHub Actions
```markdown
![Tests](https://github.com/{owner}/{repo}/actions/workflows/tests.yml/badge.svg)
![Coverage](https://codecov.io/gh/{owner}/{repo}/branch/main/graph/badge.svg)
```

### GitLab CI
```markdown
![pipeline](https://gitlab.com/{group}/{repo}/badges/main/pipeline.svg)
![coverage](https://gitlab.com/{group}/{repo}/badges/main/coverage.svg)
```

---

## 🔐 Restrições

- ✅ Gerar pipelines que rodam em ambientes clean (sem estado local).
- ✅ Usar caching para acelerar instalação de dependências.
- ✅ Separar unit tests e integration tests em jobs/stages diferentes.
- ✅ Apresentar o pipeline para aprovação antes de criar os arquivos.
- 🚫 **Proibido**: Incluir secrets/tokens hardcoded no pipeline.
- 🚫 **Proibido**: Pipelines que fazem deploy (apenas test/lint).

---

## 📤 Formato de Saída

1. **Detecção de Ambiente** (plataforma, linguagem, framework detectados)
2. **Pipeline YAML** (pronto para commit)
3. **Badges de README** (Markdown para copiar/colar)
4. **Instruções de Ativação** (como habilitar no Git provider)
