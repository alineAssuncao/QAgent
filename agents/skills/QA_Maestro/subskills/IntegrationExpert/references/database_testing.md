# Guia de Teste de Banco de Dados

## Princípios

1. **Isolamento Total**: Cada teste deve usar seu próprio dataset.
2. **Cleanup Automático**: Dados criados em testes não devem persistir.
3. **Determinismo**: Mesmos dados de entrada = mesmos resultados.
4. **Velocidade**: Preferir bancos in-memory quando possível.

---

## Estratégias por Complexidade

### Nível 1: Banco In-Memory (Preferido)
- **Quando usar**: Testes rápidos, CI/CD, projetos simples.
- **Como**: SQLite `:memory:`, H2, MongoDB Memory Server.
- **Prós**: Rápido, sem setup, completamente isolado.
- **Contras**: Pode ter diferenças de dialeto SQL.

### Nível 2: Transação com Rollback
- **Quando usar**: Precisa testar com banco real mas isolado.
- **Como**: BEGIN → teste → ROLLBACK.
- **Prós**: Usa banco real, sem resíduos.
- **Contras**: Ligeiramente mais lento.

### Nível 3: TestContainers (Docker)
- **Quando usar**: Precisa de compatibilidade exata com produção.
- **Como**: Container temporário (PostgreSQL, MySQL, Redis).
- **Prós**: Idêntico ao ambiente real.
- **Contras**: Requer Docker, mais lento.

---

## Fixtures de Dados

### Factory Pattern (Recomendado)
```python
# factories.py
def create_user(name="Default", email="default@test.com", **overrides):
    data = {"name": name, "email": email, **overrides}
    return User(**data)
```

### Seed Files
```json
// seeds/users.json
[
    {"id": 1, "name": "Admin", "role": "admin"},
    {"id": 2, "name": "User", "role": "user"}
]
```

### Builder Pattern
```python
class UserBuilder:
    def __init__(self):
        self.data = {"name": "Default", "email": "a@b.com"}
    
    def with_name(self, name): self.data["name"] = name; return self
    def with_role(self, role): self.data["role"] = role; return self
    def build(self): return User(**self.data)
```

---

## Padrões Anti (Evitar)

| Anti-padrão | Problema | Solução |
|-------------|----------|---------|
| Dados compartilhados entre testes | Testes acoplados | Factory por teste |
| Banco de dev para testes | Dados inconsistentes | Banco in-memory |
| Seeds globais | Ordem importa | Fixtures explícitas |
| Sem cleanup | Resíduos acumulam | Rollback/teardown |
