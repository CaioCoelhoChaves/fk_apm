# 08 - Testing Strategy & Observability

## Table of Contents
- [1. Spring Boot Testing Pyramid](#1-spring-boot-testing-pyramid)
- [2. Unit Testing Services with Mockito](#2-unit-testing-services-with-mockito)
- [3. Web Slice Testing (@WebMvcTest & MockMvc)](#3-web-slice-testing-webmvctest--mockmvc)
- [4. Data Slice Testing (@DataJpaTest)](#4-data-slice-testing-datajpatest)
- [5. Integration Testing with Testcontainers](#5-integration-testing-with-testcontainers)
- [6. Production Observability: Actuator & Health Probes](#6-production-observability-actuator--health-probes)
- [7. HikariCP Connection Pool Tuning](#7-hikaricp-connection-pool-tuning)

---

## 1. Spring Boot Testing Pyramid

A robust Spring Boot backend avoids testing everything via heavy `@SpringBootTest` integration tests:

1. **Domain Unit Tests** (70%): POJOs, rich domain logic, invariants. Instant execution (~1ms), zero Spring context.
2. **Slice Tests** (20%):
   - `@WebMvcTest`: Focuses solely on Controller serialization, HTTP status, and validation.
   - `@DataJpaTest`: Focuses solely on custom queries, JPA mappings, and SQL generation.
3. **Architecture Tests** (5%): ArchUnit rules preventing layer violations and cyclic dependencies.
4. **Integration Tests** (5%): `@SpringBootTest` with Testcontainers testing the whole flow against a real database.

---

## 2. Unit Testing Services with Mockito

```java
@ExtendWith(MockitoExtension.class)
class PacoteServiceTest {

    @Mock
    private PacoteRepository repository;

    @InjectMocks
    private PacoteService service;

    @Test
    void deveRetornarPacoteQuandoIdExistir() {
        UUID id = UUID.randomUUID();
        Pacote mockPacote = new Pacote("Pacote Nordeste", null);
        when(repository.findById(id)).thenReturn(Optional.of(mockPacote));

        Optional<Pacote> resultado = service.obterPacote(id);

        assertThat(resultado).isPresent();
        assertThat(resultado.get().getDescricao()).isEqualTo("Pacote Nordeste");
        verify(repository, times(1)).findById(id);
    }
}
```

---

## 3. Web Slice Testing (@WebMvcTest & MockMvc)

`@WebMvcTest` starts only the Web MVC infrastructure (controllers, converters, filters, `@RestControllerAdvice`), mocking the service layer:

```java
@WebMvcTest(PacoteController.class)
class PacoteControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PacoteService pacoteService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void deveRetornar400QuandoDescricaoForInvalida() throws Exception {
        PacoteRequest requestInvalido = new PacoteRequest("", UUID.randomUUID());

        mockMvc.perform(post("/pacotes")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(requestInvalido)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Erro de Validação"))
                .andExpect(jsonPath("$.invalidParams.descricao").exists());
    }
}
```

---

## 4. Data Slice Testing (@DataJpaTest)

`@DataJpaTest` tests persistence mappings and queries against an in-memory database:

```java
@DataJpaTest
class PacoteRepositoryTest {

    @Autowired
    private PacoteRepository repository;

    @Autowired
    private TestEntityManager entityManager;

    @Test
    void deveBuscarIdsPaginadosCorretamente() {
        Localidade loc = new Localidade("Fortaleza");
        entityManager.persist(loc);

        Pacote pacote = new Pacote("Férias de Julho", loc);
        entityManager.persist(pacote);
        entityManager.flush();

        Page<UUID> ids = repository.findIds(PageRequest.of(0, 10));

        assertThat(ids.getTotalElements()).isEqualTo(1);
        assertThat(ids.getContent()).contains(pacote.getId());
    }
}
```

---

## 5. Integration Testing with Testcontainers

For realistic multi-DBMS verification without mocking:
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class RentalIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void contextLoads() {
        assertThat(postgres.isRunning()).isTrue();
    }
}
```

---

## 6. Production Observability: Actuator & Health Probes

Enable actuator endpoints securely in `application.properties`:

```properties
management.endpoints.web.exposure.include=health,info,metrics,prometheus
management.endpoint.health.show-details=when-authorized
management.endpoint.health.probes.enabled=true
management.health.livenessstate.enabled=true
management.health.readinessstate.enabled=true
```

- `/actuator/health/liveness`: Kubernetes probe indicating whether the process is alive.
- `/actuator/health/readiness`: Kubernetes probe indicating whether database connections and caches are ready to serve traffic.

---

## 7. HikariCP Connection Pool Tuning

HikariCP is the default, high-performance connection pool in Spring Boot. Tune it for high concurrency:

```properties
# Maximum active connections to the database
spring.datasource.hikari.maximum-pool-size=20

# Minimum idle connections kept warm
spring.datasource.hikari.minimum-idle=5

# Maximum time (ms) a connection can stay idle before eviction
spring.datasource.hikari.idle-timeout=300000

# Maximum time (ms) a client will wait for a connection from pool
spring.datasource.hikari.connection-timeout=20000

# Maximum lifetime (ms) of a connection in the pool
spring.datasource.hikari.max-lifetime=1200000
```
