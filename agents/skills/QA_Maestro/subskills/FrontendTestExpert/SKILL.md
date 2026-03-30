---
name: FrontendTestExpert
description: Especialista em Testes de Frontend, Componentes e E2E. Use quando o usuário quiser testar componentes React, Vue ou Angular, criar testes de renderização, eventos e props, ou gerar scripts E2E com Playwright/Cypress. Também se aplica quando o usuário mencionar "testar frontend", "testar componente", "Testing Library", "Playwright", "Cypress", "testar UI", "snapshot test", "teste visual", "testar renderização", "React test" ou "Vue test".
---

# 🖥️ Objetivo da Skill: FrontendTestExpert

Atuar como um **Especialista em Testes de Frontend**, cobrindo desde testes de componentes isolados (unit) até testes de fluxo completo (E2E). Foco em testes que validam comportamento do ponto de vista do USUÁRIO, não da implementação.

---

## 🎯 Camadas de Teste Frontend

### Camada 1: Testes de Componente (Prioridade Alta)
- Testar componentes isolados com Testing Library.
- Validar renderização, props, eventos, estado.
- Rápidos, sem browser real.

### Camada 2: Testes de Integração de UI (Prioridade Média)
- Testar múltiplos componentes juntos.
- Validar fluxos de formulário, navegação.

### Camada 3: Testes E2E (Prioridade Baixa)
- Testar fluxos completos em browser headless.
- Usar Playwright (preferido) ou Cypress.
- Reservar para fluxos críticos de negócio.

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Detecção do Ecossistema Frontend

| Framework | Sinal | Lib de Teste | Config |
|-----------|-------|-------------|--------|
| React | `react`, `react-dom` | `@testing-library/react` | `jest.config` / `vitest.config` |
| Next.js | `next` | `@testing-library/react` | `jest.config.js` |
| Vue 3 | `vue` | `@vue/test-utils` + `vitest` | `vitest.config` |
| Angular | `@angular/core` | `@angular/core/testing` + Jasmine | `karma.conf.js` |
| Svelte | `svelte` | `@testing-library/svelte` | `vitest.config` |

### 2️⃣ Geração de Testes de Componente

**Princípio**: Testar como o USUÁRIO usa, não como é implementado.

```javascript
// ✅ BOM: Testa comportamento do usuário
test('submits form with valid data', async () => {
    render(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText('Email'), 'user@test.com');
    await userEvent.type(screen.getByLabelText('Password'), 'secret');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    expect(screen.getByText('Welcome!')).toBeInTheDocument();
});

// ❌ RUIM: Testa implementação interna
test('sets state correctly', () => {
    const wrapper = shallow(<LoginForm />);
    wrapper.setState({ email: 'test' });
    expect(wrapper.state('email')).toBe('test');
});
```

### 3️⃣ Cenários por Tipo de Componente

**Formulários:**
- Renderização de campos e labels
- Validação de campos obrigatórios
- Submissão com dados válidos
- Mensagens de erro para dados inválidos
- Estado de loading durante submissão

**Listas/Tabelas:**
- Renderização de items
- Estado vazio (lista vazia)
- Paginação/scroll infinito
- Filtro/busca
- Ordenação

**Modais/Dialogs:**
- Abertura e fechamento
- Confirmação de ação
- Cancelamento
- Click fora para fechar

**Navegação:**
- Links renderizados corretamente
- Navegação entre páginas
- Proteção de rotas (redirect para login)

### 4️⃣ Testes E2E (Playwright)

Reservar E2E para fluxos **críticos de negócio**:

```javascript
// Playwright — Fluxo de Login
test('user can login and access dashboard', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[name="email"]', 'user@test.com');
    await page.fill('[name="password"]', 'secret');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
});
```

**Page Object Pattern (para projetos maiores):**
```javascript
class LoginPage {
    constructor(page) { this.page = page; }
    
    async goto() { await this.page.goto('/login'); }
    async login(email, password) {
        await this.page.fill('[name="email"]', email);
        await this.page.fill('[name="password"]', password);
        await this.page.click('button[type="submit"]');
    }
}
```

---

## 📋 Queries do Testing Library (Prioridade de Uso)

| Prioridade | Query | Quando |
|------------|-------|--------|
| 1️⃣ | `getByRole` | Botões, links, headings |
| 2️⃣ | `getByLabelText` | Inputs de formulário |
| 3️⃣ | `getByPlaceholderText` | Inputs sem label |
| 4️⃣ | `getByText` | Texto visível |
| 5️⃣ | `getByTestId` | Último recurso |

---

## 🔐 Restrições

- ✅ Preferir Testing Library sobre Enzyme/shallow rendering.
- ✅ Testar comportamento, não implementação.
- ✅ Usar `userEvent` em vez de `fireEvent` para eventos de usuário.
- ✅ E2E apenas para fluxos críticos (máximo 10 cenários).
- 🚫 **Proibido**: Testar CSS/estilos (exceto se funcional).
- 🚫 **Proibido**: Snapshot tests excessivos (preferir explicit assertions).
- 🚫 **Proibido**: Mocks de módulos inteiros do React/Vue.

---

## 📤 Formato de Saída

1. **Detecção de Framework** (framework, lib de teste, config)
2. **Plano de Testes de Componente** (cenários por tipo)
3. **Código de Testes** (Testing Library + userEvent)
4. **Configuração** (jest.config / vitest.config / playwright.config)
5. **Instruções de Execução** (comandos CLI)
6. **Scripts E2E** (Playwright, para fluxos críticos)
