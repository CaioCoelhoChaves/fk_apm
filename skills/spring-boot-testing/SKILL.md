---
name: spring-boot-testing
description: Testing strategies, test slice optimization, and production observability for Spring Boot 3.x+ and Java 17/21+. Use this skill when designing automated test suites following the testing pyramid, writing fast unit tests for domain POJOs, testing web controllers with @WebMvcTest and MockMvc, verifying persistence layers with @DataJpaTest, configuring realistic database tests with Testcontainers, or configuring production health indicators and metrics with Spring Boot Actuator.
allowed-tools: Read,Glob,Grep,Write,Edit,Bash
---

# Spring Boot Testing & Observability

An engineering guide and operational blueprint for building fast, reliable, and maintainable automated test suites and production observability in **Spring Boot 3.x+** and **Java 17/21+**.

Synthesizes the Testing Pyramid, slice-based isolation, Testcontainers integration testing, and Spring Boot Actuator metrics.

---

## Core Non-Negotiable Standards

1. **Strict Testing Pyramid**:
   - **Unit Tests (POJOs / Domain)**: ~1ms execution time. Test business invariants, state transitions, and calculations in pure Java without booting the Spring container.
   - **Slice Tests (`@WebMvcTest`, `@DataJpaTest`)**: Fast, narrowly scoped component tests. Boot only the targeted slice of the application context.
   - **Integration / End-to-End Tests (`@SpringBootTest`, Testcontainers)**: Full application context tests reserved for critical end-to-end flows and true database interaction. Avoid over-relying on `@SpringBootTest` for simple assertions.
   - See [references/01-testing-and-observability.md](references/01-testing-and-observability.md).

2. **Web Slice Testing (`@WebMvcTest`)**:
   - Test HTTP controllers with `@WebMvcTest(MyController.class)`.
   - Mock collaborators using `@MockBean` (or `@MockitoBean` in Spring Boot 3.4+).
   - Verify HTTP status codes, headers, and JSON responses using `MockMvc` and `jsonPath()`.
   - Verify that RFC 7807 error structures return status `400 Bad Request` or `422 Unprocessable Content` when requests fail bean validation.

3. **Persistence Slice Testing (`@DataJpaTest`)**:
   - Test Spring Data JPA repositories with `@DataJpaTest`.
   - Validates custom queries, `@Query` annotations, pagination, and database mapping without loading web layers.
   - Use `@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)` when pairing with real databases via Testcontainers.

4. **Production Observability & Actuator**:
   - Include `spring-boot-starter-actuator` in all production services.
   - Expose health, readiness, and liveness endpoints for Kubernetes: `/actuator/health/liveness`, `/actuator/health/readiness`.
   - Write custom `HealthIndicator` beans for external dependencies (e.g., payment gateways, messaging brokers).

---

## Step-by-Step Workflow

### Step 1: Pure Domain Unit Testing
1. Instantiate domain entities with `new`:
   ```java
   @Test
   void shouldPreventHiringWithNegativePrice() {
       Pacote pacote = new Pacote("Pacote Verão");
       assertThatThrownBy(() -> pacote.contratar(-100.0))
           .isInstanceOf(IllegalArgumentException.class)
           .hasMessageContaining("Preço deve ser positivo");
   }
   ```
2. Assert assertions execute in milliseconds without Spring annotations.

### Step 2: Controller Slice Testing with MockMvc
1. Declare slice test:
   ```java
   @WebMvcTest(AluguelController.class)
   class AluguelControllerTest {
       @Autowired private MockMvc mockMvc;
       @MockBean private AluguelService aluguelService;

       @Test
       void shouldReturn201WhenCreated() throws Exception {
           UUID id = UUID.randomUUID();
           when(aluguelService.criar(any())).thenReturn(new AluguelResponse(id));

           mockMvc.perform(post("/alugueis")
                   .contentType(MediaType.APPLICATION_JSON)
                   .content("{\"clienteId\":\"" + id + "\"}"))
               .andExpect(status().isCreated())
               .andExpect(header().exists("Location"));
       }
   }
   ```

### Step 3: Persistence Slice Testing with @DataJpaTest
1. Test custom repository queries:
   ```java
   @DataJpaTest
   class AluguelRepositoryTest {
       @Autowired private AluguelRepository repository;
       @Autowired private TestEntityManager entityManager;

       @Test
       void shouldFindIdsWithPagination() {
           Page<UUID> ids = repository.findIds(PageRequest.of(0, 10));
           assertThat(ids).isNotNull();
       }
   }
   ```
2. Consult [references/01-testing-and-observability.md](references/01-testing-and-observability.md).

---

## Quick Reference Commands

| Task | Command |
| :--- | :--- |
| **Run all tests** | `./mvnw clean test` |
| **Run slice test only** | `./mvnw test -Dtest=AluguelControllerTest` |
| **Run repository tests only** | `./mvnw test -Dtest=*RepositoryTest` |
| **Inspect Actuator Health** | `curl -i http://localhost:8080/actuator/health` |
