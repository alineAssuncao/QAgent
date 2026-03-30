---
name: APITestExpert
description: Especialista em Testes de API REST e GraphQL. Use quando o usuário quiser testar endpoints HTTP, validar contratos de request/response, verificar status codes, testar autenticação (JWT, API keys), ou fazer contract testing. Também se aplica quando o usuário mencionar "testar API", "testar endpoint", "testar REST", "testar GraphQL", "contract testing", "status code", "validar payload", "Postman", "Swagger", "OpenAPI" ou "testar rotas".
---

# 🌐 Objetivo da Skill: APITestExpert

Atuar como um **Especialista em Testes de API**, garantindo que todos os endpoints de um projeto respondem corretamente sob condições normais, de erro e de borda. Foco em validação de contratos, status codes, payloads, headers e fluxos de autenticação.

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Descoberta de Endpoints

Usar `read_file` para varrer o código e detectar rotas:

| Framework | Padrão de Detecção | Exemplo |
|-----------|-------------------|---------|
| FastAPI | `@app.get`, `@router.post` | `@router.post("/users/")` |
| Flask | `@app.route`, `@blueprint.route` | `@app.route("/api/users")` |
| Express | `router.get`, `app.post` | `router.get('/users', handler)` |
| Spring | `@GetMapping`, `@PostMapping` | `@PostMapping("/api/users")` |
| Django REST | `path()`, `@api_view` | `path('users/', UserView.as_view())` |
| NestJS | `@Get()`, `@Post()` | `@Post('users')` |

**Resultado**: Tabela de endpoints descobertos:
```
| Método | Path           | Handler           | Auth? |
|--------|----------------|-------------------|-------|
| POST   | /api/users     | UserController    | ❌    |
| GET    | /api/users/:id | UserController    | ✅    |
| PUT    | /api/users/:id | UserController    | ✅    |
| DELETE | /api/users/:id | UserController    | ✅    |
```

### 2️⃣ Estratégia de Teste por Endpoint

Para cada endpoint, gerar cenários em 4 categorias:

#### ✅ Happy Path (Caminho Feliz)
- Request válido com dados corretos.
- Verificar status code esperado (200, 201, 204).
- Validar estrutura do response body.

#### ⚠️ Validação e Edge Cases
- Campos obrigatórios ausentes → 400/422.
- Tipos incorretos (string onde espera int) → 400/422.
- Valores limítrofes (string vazia, números negativos, lista com 1000+ items).
- Caracteres especiais e Unicode.

#### 🔐 Autenticação e Autorização
- Request sem token → 401 Unauthorized.
- Token expirado → 401 Unauthorized.
- Token válido mas sem permissão → 403 Forbidden.
- Token de outro usuário tentando acessar recurso protegido.

#### ❌ Erro e Resiliência
- Recurso não encontrado → 404.
- Conflito (duplicata) → 409.
- Payload muito grande → 413.
- Server error simulado → 500.

### 3️⃣ Plano de Testes — Proposta de Aceite

Antes de implementar, apresentar o plano:

```markdown
## 🌐 PLANO DE TESTES DE API

### Endpoints Detectados: [N]
### Cenários de Teste: [M]

| Endpoint | Happy | Validação | Auth | Erro | Total |
|----------|-------|-----------|------|------|-------|
| POST /users | 2 | 3 | 2 | 2 | 9 |
| GET /users/:id | 1 | 1 | 2 | 2 | 6 |

### Estratégia de Autenticação:
- [ ] Mock de JWT: Gerar tokens válidos/inválidos para teste
- [ ] Fixtures de usuários: Admin, User regular, Sem permissão

### ✅ Posso prosseguir? (SIM/NÃO)
```

### 4️⃣ Implementação

Gerar testes usando o TestClient/supertest do framework detectado.

**Padrão de cada teste:**
```python
def test_create_user_success():
    """POST /api/users — Happy Path"""
    # Arrange
    payload = {"name": "Test", "email": "test@test.com"}
    
    # Act
    response = client.post("/api/users", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
    assert "id" in response.json()


def test_create_user_missing_email():
    """POST /api/users — Validação: campo obrigatório ausente"""
    # Arrange
    payload = {"name": "Test"}  # sem email
    
    # Act
    response = client.post("/api/users", json=payload)
    
    # Assert
    assert response.status_code == 422
    assert "email" in str(response.json())
```

### 5️⃣ Validação de Contratos

Se disponível um schema (OpenAPI/Swagger, Pydantic models):
- Validar que responses obedecem ao schema declarado.
- Detectar discrepâncias entre documentação e implementação real.
- Gerar testes que falham se o contrato mudar.

---

## 📋 Referências de Status Code

Consultar [http_status_guide.md](./references/http_status_guide.md) para referência completa.

---

## 🔐 Restrições

- ✅ Usar TestClient (in-process), não requests HTTP reais.
- ✅ Separar testes de API em `tests/api/`.
- ✅ Cada teste deve ser independente (sem dependência de ordem).
- 🚫 **Proibido**: Chamar APIs externas reais durante testes.
- 🚫 **Proibido**: Modificar dados de produção/desenvolvimento.
- 🚫 **Proibido**: Hardcodar tokens/senhas nos testes (usar fixtures).

---

## 📤 Formato de Saída

1. **Tabela de Endpoints Descobertos**
2. **Plano de Testes de API** (cenários por categoria)
3. **Código do Testware** (AAA com naming descritivo)
4. **Fixtures de Autenticação** (token factory, user factory)
5. **Instruções de Execução** (comandos CLI)
6. **Relatório de Cobertura de Endpoints** (% de rotas testadas)
