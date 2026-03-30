# Guia de Status Codes HTTP para Testes de API

## Códigos de Sucesso (2xx)

| Code | Nome | Quando Usar | Teste |
|------|------|-------------|-------|
| 200 | OK | GET, PUT, PATCH com body de resposta | Verificar body |
| 201 | Created | POST que cria recurso | Verificar Location header + body |
| 204 | No Content | DELETE, PUT sem body de resposta | Verificar body vazio |

## Códigos de Redirecionamento (3xx)

| Code | Nome | Quando Usar | Teste |
|------|------|-------------|-------|
| 301 | Moved Permanently | URL mudou definitivamente | Verificar Location |
| 302 | Found | Redirecionamento temporário | Verificar Location |
| 304 | Not Modified | Cache válido | Verificar ETag/If-Modified-Since |

## Códigos de Erro do Cliente (4xx)

| Code | Nome | Quando Usar | Teste |
|------|------|-------------|-------|
| 400 | Bad Request | JSON malformado, tipo errado | Enviar payload inválido |
| 401 | Unauthorized | Sem autenticação | Request sem token |
| 403 | Forbidden | Autenticado mas sem permissão | Token válido sem role |
| 404 | Not Found | Recurso inexistente | ID/path inexistente |
| 405 | Method Not Allowed | Método HTTP errado | DELETE em rota GET-only |
| 409 | Conflict | Duplicata, conflito de estado | Criar recurso duplicado |
| 413 | Payload Too Large | Body excede limite | Payload muito grande |
| 422 | Unprocessable Entity | Validação de negócio falhou | Campos obrigatórios faltando |
| 429 | Too Many Requests | Rate limiting | Múltiplas requests rápidas |

## Códigos de Erro do Servidor (5xx)

| Code | Nome | Quando Usar | Teste |
|------|------|-------------|-------|
| 500 | Internal Server Error | Erro inesperado no servidor | Mock que lança exceção |
| 502 | Bad Gateway | Proxy/gateway falhou | Mock de serviço downstream |
| 503 | Service Unavailable | Serviço temporariamente fora | Mock de dependência |
| 504 | Gateway Timeout | Timeout em serviço upstream | Mock com delay |

---

## Cenários Comuns de Teste por Endpoint

### POST (Criação)
```
✅ 201 — Dados válidos → recurso criado
❌ 400 — JSON malformado
❌ 401 — Sem autenticação
❌ 403 — Sem permissão
❌ 409 — Recurso já existe (email duplicado)
❌ 422 — Campos obrigatórios ausentes
```

### GET (Leitura)
```
✅ 200 — Recurso encontrado
✅ 200 — Lista paginada (verificar meta/pagination)
❌ 401 — Sem autenticação
❌ 404 — ID inexistente
```

### PUT/PATCH (Atualização)
```
✅ 200 — Atualização bem-sucedida
❌ 400 — Dados inválidos
❌ 401 — Sem autenticação
❌ 403 — Atualizando recurso de outro usuário
❌ 404 — Recurso não encontrado
❌ 409 — Conflito de versão (optimistic locking)
```

### DELETE (Remoção)
```
✅ 204 — Removido com sucesso
❌ 401 — Sem autenticação
❌ 403 — Sem permissão para remover
❌ 404 — Recurso não encontrado
```

---

## Headers Importantes para Testar

| Header | Teste |
|--------|-------|
| `Content-Type` | Deve ser `application/json` para APIs JSON |
| `Authorization` | `Bearer <token>` para endpoints protegidos |
| `Location` | Presente em responses 201 (link para recurso criado) |
| `X-Request-Id` | Rastreabilidade (se implementado) |
| `Cache-Control` | Política de cache correta |
| `CORS headers` | `Access-Control-Allow-Origin` etc. |

---

## Validação de Payload

### Schema Validation (Pydantic/JSON Schema)
```python
# Verificar que o response obedece ao schema
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

def test_user_response_schema():
    response = client.get("/api/users/1")
    UserResponse(**response.json())  # Valida schema
```

### Verificações Comuns
```python
# Tipo correto
assert isinstance(response.json()["id"], int)

# Campo presente
assert "created_at" in response.json()

# Lista não vazia
assert len(response.json()["items"]) > 0

# Paginação
assert "total" in response.json()
assert "page" in response.json()
```
