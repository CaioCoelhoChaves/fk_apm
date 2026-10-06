---
name: spring-boot-api-resilience
description: REST API design, RFC 7807 problem details error handling, and distributed resilience patterns for Spring Boot 3.x+. Use this skill when building REST controllers, validating requests with Jakarta Bean Validation, returning standardized ProblemDetail (application/problem+json) exceptions via @RestControllerAdvice, designing immutable DTOs with Java records, implementing API idempotency (X-Idempotency-Id header and database constraints), retry policies with Spring Retry, or orchestrating distributed operations with Sagas and Watchdog schedulers.
allowed-tools: Read,Glob,Grep,Write,Edit,Bash
---

# Spring Boot API Design & Distributed Resilience

An engineering guide and operational blueprint for designing modern, robust, and resilient HTTP APIs with **Spring Boot 3.x+** and **Java 17/21+**.

Synthesizes Richardson Maturity Level 2 RESTful standards, RFC 7807 Problem Details error handling, idempotent distributed operations, and self-healing background reconciliation workers.

---

## Core Non-Negotiable Standards

1. **REST APIs & Immutable Record DTOs**:
   - Reach Richardson Maturity Level 2 (appropriate HTTP verbs, URI nouns, and HTTP status codes: `201 Created` with `Location` header, `204 No Content` for deletions, `200 OK` for reads/updates).
   - Never expose JPA entities in controller endpoints. Always transfer data via Java `record` DTOs to preserve encapsulation and decouple presentation from database schema.
   - Enforce Jakarta Bean Validation (`@NotBlank`, `@Size`, `@Positive`, `@NotNull`, `@Valid`) at controller entrypoints.
   - For paginated collections, expose the total count via the `X-Total-Count` HTTP response header.
   - See [references/01-rest-api-design-and-validation.md](references/01-rest-api-design-and-validation.md).

2. **Standardized RFC 7807 Problem Details**:
   - Always return errors formatted as `application/problem+json` according to RFC 7807.
   - Implement a centralized `@RestControllerAdvice` utilizing Spring Boot 3's native `ProblemDetail` API.
   - Categorize errors with descriptive `type` URIs, human-readable `title`, specific HTTP `status`, and contextual custom properties (e.g., `invalidParams` mapping field names to validation error messages).
   - See [references/01-rest-api-design-and-validation.md](references/01-rest-api-design-and-validation.md).

3. **Distributed Resilience & Idempotency**:
   - HTTP network interactions do NOT propagate ACID transactions across boundaries.
   - Require an `X-Idempotency-Id` HTTP header on critical state-changing POST/PUT requests.
   - Back idempotency tokens with unique constraints in the database (`tx_id` / `idempotency_key`).
   - Use `@Retryable(retryFor = DataIntegrityViolationException.class)` to safely handle race conditions and concurrent double-submits.
   - Design operations to be commutative whenever possible.
   - Implement scheduled **Watchdog** background workers (`@Scheduled`) to audit and auto-reconcile transient stuck states (e.g., `PENDING` transactions exceeding timeout thresholds).
   - See [references/02-resilience-and-distributed-patterns.md](references/02-resilience-and-distributed-patterns.md).

---

## Step-by-Step Workflow

### Step 1: DTO Modeling & Jakarta Validation
1. Define immutable request and response models as Java `record`s:
   ```java
   public record CriarAluguelRequest(
       @NotNull UUID clienteId,
       @NotNull UUID veiculoId,
       @NotNull @Future Instant dataInicio,
       @NotNull @Future Instant dataFim
   ) {}
   ```
2. Annotate `@RequestBody @Valid CriarAluguelRequest request` in controller methods.

### Step 2: Global Exception Handling (RFC 7807)
1. Copy `GlobalExceptionHandler.java` from `assets/templates/` into your `config` package.
2. Ensure handlers cover `MethodArgumentNotValidException`, `IllegalArgumentException`, and catch-all `Exception`.
3. Test that error responses return content type `application/problem+json`.

### Step 3: Idempotent Endpoints & Sagas
1. Require `X-Idempotency-Id` on write operations:
   ```java
   @PostMapping
   public ResponseEntity<AluguelResponse> criar(
       @RequestHeader("X-Idempotency-Id") String idempotencyId,
       @RequestBody @Valid CriarAluguelRequest request
   ) {
       AluguelResponse response = aluguelService.criarIdempotente(idempotencyId, request);
       URI location = URI.create("/alugueis/" + response.id());
       return ResponseEntity.created(location).body(response);
   }
   ```
2. Configure Spring Retry with `@EnableRetry` in a `@Configuration` class and apply `@Retryable` at service boundaries.
3. Configure scheduled Watchdog tasks:
   ```java
   @Scheduled(fixedDelay = 60000)
   public void reconciliarTransacoesPendentes() {
       watchdogService.reconciliarPendentes();
   }
   ```
4. Consult [references/02-resilience-and-distributed-patterns.md](references/02-resilience-and-distributed-patterns.md).

---

## Reusable Asset Templates

- `assets/templates/GlobalExceptionHandler.java`: RFC 7807 Problem Details controller advice covering bean validation, business rule violations, and unexpected exceptions.

---

## Quick Reference Commands

| Task | Command |
| :--- | :--- |
| **Run API slice tests** | `./mvnw test -Dtest=*ControllerTest` |
| **Check Actuator Health** | `curl -i http://localhost:8080/actuator/health` |
