# Catálogo de Refatorações para Testabilidade

## Refatorações por Prioridade

### 🔴 Prioridade Alta (Desbloqueia testes)

#### 1. Dependency Injection (Injeção de Dependência)
**Problema**: Classe instancia suas deps → impossível injetar mocks.
**Antes**: `self.db = Database()`
**Depois**: `def __init__(self, db: Database): self.db = db`
**Linguagens**: Todas

#### 2. Extract Interface (Extrair Interface/Abstração)
**Problema**: Código acoplado a implementação concreta.
**Antes**: `def process(self, gateway: StripeGateway)`
**Depois**: `def process(self, gateway: PaymentGateway)` (ABC)
**Linguagens**: Python, Java, C#, TypeScript

#### 3. Remove Global State (Remover Estado Global)
**Problema**: Singletons e variáveis de módulo impossibilitam isolamento.
**Antes**: `config = GlobalConfig.instance()`
**Depois**: `def __init__(self, config: Config): self.config = config`
**Linguagens**: Todas

---

### 🟠 Prioridade Média (Melhora qualidade dos testes)

#### 4. Extract Method (Extrair Método)
**Problema**: Método longo com múltiplas responsabilidades.
**Regra**: Se CC > 10 ou LOC > 50, extrair.
**Linguagens**: Todas

#### 5. Extract Class (Extrair Classe)
**Problema**: God Class com muitas responsabilidades.
**Regra**: Se classe tem >5 dependências ou >300 LOC.
**Linguagens**: Todas

#### 6. Replace Conditional with Polymorphism
**Problema**: Cadeias if/elif/switch longas.
**Regra**: Se >3 branches com mesma estrutura.
**Linguagens**: Todas (OOP)

---

### 🟡 Prioridade Baixa (Melhora manutenibilidade)

#### 7. Extract Constant (Extrair Constante)
**Problema**: Magic numbers/strings espalhados.
**Linguagens**: Todas

#### 8. Introduce Parameter Object
**Problema**: Método com >5 parâmetros.
**Antes**: `def create(name, email, age, role, dept)`
**Depois**: `def create(user: UserDTO)`
**Linguagens**: Todas

#### 9. Replace Temp with Query
**Problema**: Variáveis temporárias desnecessárias.
**Linguagens**: Todas

---

## Padrões de Testabilidade

### Padrão 1: Separação Comando-Consulta (CQS)
```python
# Métodos que RETORNAM algo não devem ter EFEITOS COLATERAIS
# Métodos que CAUSAM efeitos não devem RETORNAR dados
def get_balance(self) -> float:    # Query: retorna, sem efeitos
    return self.balance

def withdraw(self, amount: float): # Command: altera, sem return
    self.balance -= amount
```

### Padrão 2: Tell, Don't Ask
```python
# RUIM: Perguntar estado e decidir fora
if order.get_status() == "pending":
    order.set_status("processing")

# BOM: Delegar decisão para o objeto
order.process()  # internamente decide se pode
```

### Padrão 3: Humble Object
```python
# Separar lógica testável de infraestrutura não-testável

# Humble Object (fino, difícil de testar → OK)
class FileProcessor:
    def process(self, filepath):
        data = open(filepath).read()   # I/O
        result = self.logic.transform(data)  # delega
        open(filepath + '.out', 'w').write(result)  # I/O

# Lógica pura (fácil de testar)
class TransformLogic:
    def transform(self, data: str) -> str:
        return data.upper()  # lógica pura, sem I/O
```
