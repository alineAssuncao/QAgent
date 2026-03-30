# Padrões de Teste de Integração por Framework

## Python

### FastAPI + pytest
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_user():
    # Integração: Controller → Service → Repository → DB
    response = client.post("/users/", json={"name": "Test", "email": "test@test.com"})
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```
Dependências: `pip install httpx pytest`

### Flask + pytest
```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

def test_login_flow(client):
    # Integração: Route → Auth Service → User Repository
    response = client.post("/auth/login", json={"email": "a@b.com", "password": "123"})
    assert response.status_code == 200
    assert "token" in response.json
```
Dependências: `pip install pytest`

### Django + pytest-django
```python
import pytest
from django.test import Client

@pytest.mark.django_db
def test_order_workflow():
    client = Client()
    # Integração: View → Serializer → Model → DB
    response = client.post("/api/orders/", {"product": "Widget", "quantity": 5})
    assert response.status_code == 201
```
Dependências: `pip install pytest-django`

---

## JavaScript / TypeScript

### Express + supertest
```javascript
const request = require('supertest');
const app = require('../src/app');

describe('User Integration', () => {
    it('should create and retrieve user', async () => {
        const createRes = await request(app)
            .post('/api/users')
            .send({ name: 'Test', email: 'test@test.com' });
        expect(createRes.statusCode).toBe(201);

        const getRes = await request(app)
            .get(`/api/users/${createRes.body.id}`);
        expect(getRes.statusCode).toBe(200);
        expect(getRes.body.name).toBe('Test');
    });
});
```
Dependências: `npm install --save-dev supertest jest`

### NestJS + Testing Module
```typescript
import { Test } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('AppController (e2e)', () => {
    let app: INestApplication;

    beforeAll(async () => {
        const moduleFixture = await Test.createTestingModule({
            imports: [AppModule],
        }).compile();
        app = moduleFixture.createNestApplication();
        await app.init();
    });

    it('/users (POST)', () => {
        return request(app.getHttpServer())
            .post('/users')
            .send({ name: 'Test' })
            .expect(201);
    });
});
```
Dependências: `npm install --save-dev @nestjs/testing supertest`

---

## Java

### Spring Boot + MockMvc
```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void shouldCreateAndRetrieveUser() throws Exception {
        String userJson = "{\"name\":\"Test\",\"email\":\"test@test.com\"}";
        
        MvcResult result = mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(userJson))
                .andExpect(status().isCreated())
                .andReturn();
        
        String id = JsonPath.read(result.getResponse().getContentAsString(), "$.id");
        
        mockMvc.perform(get("/api/users/" + id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Test"));
    }
}
```
Dependências: `spring-boot-starter-test`

---

## Banco de Dados In-Memory

### SQLite In-Memory (Python)
```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

### H2 Database (Java)
```properties
# application-test.properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop
```

### MongoDB Memory Server (Node.js)
```javascript
const { MongoMemoryServer } = require('mongodb-memory-server');

let mongoServer;
beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    process.env.MONGO_URI = mongoServer.getUri();
});
afterAll(async () => { await mongoServer.stop(); });
```
