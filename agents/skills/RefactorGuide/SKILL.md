---
name: RefactorGuide
description: Guia de Refatoração para Testabilidade. Use quando o código for difícil de testar, tiver alta complexidade ciclomática, God Classes, dependências ocultas ou acoplamento forte. Identifica problemas de design que impedem a criação de bons testes e propõe refatorações seguras (Extract Method, Dependency Injection, Extract Interface) antes da automação. Também se aplica quando o usuário mencionar "refatorar", "código difícil de testar", "melhorar testabilidade", "design patterns", "desacoplar", "God Class" ou "injeção de dependência".
---

# 🔧 Objetivo da Skill: RefactorGuide

Atuar como um **Consultor de Design para Testabilidade**, identificando barreiras estruturais que impedem a criação de testes eficientes e propondo refatorações seguras, incrementais e com aprovação do usuário.

---

## 🎯 Princípio Central

> "Não force testes em código ruim. Melhore o código para que os testes sejam naturais."

A maioria dos problemas de teste não é um problema de teste — é um problema de design. Esta skill resolve a CAUSA (design) e não o SINTOMA (teste difícil).

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Diagnóstico de Testabilidade

Usar `read_file` para analisar o código e identificar barreiras:

**Checklist de Testabilidade:**
- [ ] As classes recebem dependências via construtor? (DI)
- [ ] Os métodos têm responsabilidade única? (SRP)
- [ ] Há separação entre lógica de negócio e infraestrutura?
- [ ] As dependências externas estão atrás de interfaces/abstrações?
- [ ] Os métodos retornam valores em vez de causar efeitos colaterais?
- [ ] O estado global é evitado (singletons, variáveis de módulo)?

### 2️⃣ Classificação de Problemas

| Problema | Severidade | Refatoração |
|----------|-----------|-------------|
| God Class (>300 LOC, >5 deps) | 🔴 Crítico | Extract Class |
| Instanciação direta de deps | 🔴 Crítico | Dependency Injection |
| Deps ocultas (globals, singletons) | 🔴 Crítico | Tornar explícitas |
| Método longo (>50 LOC, CC>10) | 🟠 Alto | Extract Method |
| Acoplamento temporal | 🟠 Alto | Encapsular em construtor |
| Feature Envy | 🟡 Médio | Move Method |
| Primitive Obsession | 🟡 Médio | Value Objects |
| Magic Numbers | 🟢 Baixo | Extract Constant |

### 3️⃣ Plano de Refatoração — Proposta de Aceite

> [!CAUTION]
> **NUNCA modificar código sem aprovação explícita do usuário.**

Antes de qualquer mudança, apresentar um plano:

```markdown
## 🔧 PLANO DE REFATORAÇÃO

### Arquivo: src/services/payment_service.py
### Problemas Detectados: 3

1. **God Class** (320 LOC, 8 dependências)
   - 💊 Ação: Extrair `PaymentValidator` e `PaymentNotifier`
   - 📊 Impacto: Reduz CC de 22 para ~8 por classe
   - ⚠️ Risco: Médio (mover lógica entre classes)

2. **Dependência oculta** (`Database()` instanciada direto)
   - 💊 Ação: Injeção via construtor (`__init__(self, db: Database)`)
   - 📊 Impacto: Permite injetar mock nos testes
   - ⚠️ Risco: Baixo (mudança isolada)

3. **Método longo** (`process_payment`, 85 linhas)
   - 💊 Ação: Extrair `_validate_card()`, `_charge()`, `_notify()`
   - 📊 Impacto: CC de 15 para ~5 por método
   - ⚠️ Risco: Baixo (decomposição simples)

### ✅ Posso prosseguir? (SIM/NÃO)
```

### 4️⃣ Execução Incremental

Aplicar refatorações uma por vez:
1. Fazer a menor mudança possível.
2. Verificar se testes existentes ainda passam (se houver).
3. Confirmar com o usuário antes da próxima.

### 5️⃣ Verificação Pós-Refatoração

- Executar testes existentes via `git_manage run_tests`.
- Confirmar que nenhum comportamento foi alterado.
- Atualizar mapa de testabilidade.

---

## 📚 Catálogo de Refatorações

### Extract Method
```python
# ANTES: Método com CC=15
def process_order(self, order):
    # validação (20 linhas)
    # cálculo (15 linhas)
    # persistência (10 linhas)
    # notificação (10 linhas)

# DEPOIS: CC=3 cada
def process_order(self, order):
    self._validate(order)
    total = self._calculate(order)
    self._persist(order, total)
    self._notify(order)
```

### Dependency Injection
```python
# ANTES: Impossível mockar
class OrderService:
    def __init__(self):
        self.db = Database()          # acoplamento
        self.mailer = SmtpMailer()    # acoplamento

# DEPOIS: Testável com mocks
class OrderService:
    def __init__(self, db: Database, mailer: Mailer):
        self.db = db
        self.mailer = mailer
```

### Extract Interface
```python
# ANTES: Acoplado a implementação concreta
class PaymentService:
    def __init__(self, gateway: StripeGateway):
        self.gateway = gateway

# DEPOIS: Desacoplado via abstração
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float): pass

class PaymentService:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
```

### Replace Conditional with Polymorphism
```python
# ANTES: Switch/if chain
def calculate_discount(self, customer_type):
    if customer_type == "regular": return 0.05
    elif customer_type == "premium": return 0.15
    elif customer_type == "vip": return 0.25

# DEPOIS: Strategy Pattern
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self) -> float: pass

class RegularDiscount(DiscountStrategy):
    def calculate(self) -> float: return 0.05
```

---

## 🔐 Restrições

- ✅ Sempre preservar comportamento existente (refactoring, não rewrite).
- ✅ Executar testes existentes antes e depois de cada mudança.
- ✅ Uma refatoração por vez (incremental).
- 🚫 **Proibido**: Alterar APIs públicas sem aprovação explícita.
- 🚫 **Proibido**: Remover funcionalidade durante refatoração.
- 🚫 **Proibido**: Aplicar múltiplas refatorações sem checkpoint intermediário.

---

## 📤 Formato de Saída

1. **Diagnóstico de Testabilidade** (checklist com scores)
2. **Plano de Refatoração** (problemas + ações + riscos)
3. **Código Refatorado** (diffs claros)
4. **Resultado de Verificação** (testes existentes passando)
5. **Mapa de Testabilidade Atualizado** (antes/depois)
