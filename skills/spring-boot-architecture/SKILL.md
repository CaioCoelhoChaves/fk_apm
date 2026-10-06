---
name: spring-boot-architecture
description: Architectural governance, layered boundaries, and domain modeling for Spring Boot 3.x+ and Java 17/21+. Use this skill when structuring backend layers (Controller -> Service -> Repository -> Domain), enforcing architectural rules with ArchUnit, eliminating field injection (@Autowired) in favor of immutable constructor injection, designing rich anti-anemic domain models with defensive encapsulation (Collections.unmodifiableList), protecting business invariants, or mapping polymorphic domain inheritance. Always trigger this skill for architecture design, package structuring, or ArchUnit test creation in Spring Boot.
allowed-tools: Read,Glob,Grep,Write,Edit,Bash
---

# Spring Boot Architecture & Governance

An architectural guide and operational blueprint for designing, structuring, and governing enterprise backend applications with **Spring Boot 3.x+** and **Java 17/21+**.

Enforces foundational software engineering standards: rich domain models, strict layered boundaries, automated bytecode governance via ArchUnit, and defensive object-oriented encapsulation.

---

## Core Non-Negotiable Standards

1. **Rich Domain Model (Anti-Anemic)**:
   - Entities must encapsulate both state and behavior. Never reduce entities to dumb data bags with indiscriminate public getters and setters.
   - Enforce business invariants at mutation boundaries (e.g., `cliente.contratar(pacote)`, `pedido.adicionarItem(item)`).
   - Use rich enums with `@Enumerated(EnumType.STRING)` for lifecycle and status states.
   - See [references/02-domain-modeling-and-oop.md](references/02-domain-modeling-and-oop.md).

2. **Defensive Programming & Encapsulation**:
   - Never expose raw mutable collection references. Always return unmodifiable views: `Collections.unmodifiableList(items)`.
   - Protect inputs defensively; guarantee null-safety and validate domain constraints before mutating state.
   - For inheritance, prefer `InheritanceType.JOINED` combined with polymorphic Jackson mapping (`@JsonTypeInfo`, `@JsonSubTypes`).

3. **Strict Layered Architecture & ArchUnit Governance**:
   - Dependencies flow strictly downwards: `Controller` → `Service` → `Repository` → `Domain`.
   - Controllers must **never** call Repositories directly. All operations pass through the Service/Use Case layer.
   - Enforce architectural boundaries through automated bytecode checks using **ArchUnit** in the test suite.
   - See [references/03-architecture-and-archunit.md](references/03-architecture-and-archunit.md).

4. **Mandatory Constructor Injection**:
   - Field injection (`@Autowired` on private fields) is strictly prohibited. It harms testability and promotes mutability.
   - Always declare dependencies as `private final` and inject them via the constructor. Spring Boot autowires single-constructor classes automatically without requiring annotations.

---

## Step-by-Step Workflow

### Step 1: Project Structuring & Package Layout
1. Verify package structure follows canonical layers:
   ```text
   src/main/java/br/com/empresa/<modulo>/
   ├── config/          # Spring @Configuration classes
   ├── controller/      # REST endpoints (@RestController)
   ├── dto/             # Request & Response Java records
   ├── service/         # Business logic & orchestration (@Service)
   ├── repository/      # Spring Data JPA interfaces (@Repository)
   └── domain/          # Entities, Value Objects, Enums
   ```
2. Check `application.properties`: Ensure `spring.jpa.open-in-view=false` is explicitly set to prevent session leaks outside transactions.
3. Consult [references/01-bootstrap-and-configuration.md](references/01-bootstrap-and-configuration.md).

### Step 2: Domain Entity & Invariant Design
1. Define entities with package-private or `protected` no-arg constructors (required by JPA) and public factory or descriptive business constructors.
2. Replace public setters with intent-revealing business methods that validate invariants.
3. Wrap collection getters in `Collections.unmodifiableList(this.items)`.
4. Consult [references/02-domain-modeling-and-oop.md](references/02-domain-modeling-and-oop.md).

### Step 3: Layered Architecture & ArchUnit Verification
1. Structure beans with constructor injection:
   ```java
   @RestController
   public class PacoteController {
       private final PacoteService pacoteService;

       public PacoteController(PacoteService pacoteService) {
           this.pacoteService = pacoteService;
       }
   }
   ```
2. Copy `DemoArchUnitTest.java` from `assets/templates/` into `src/test/java/<base-package>/ApplicationArchUnitTest.java`.
3. Replace the `{{PACKAGE_NAME}}` placeholder with your application's root package name.
4. Execute ArchUnit tests:
   ```bash
   ./mvnw test -Dtest=ApplicationArchUnitTest
   ```
5. Consult [references/03-architecture-and-archunit.md](references/03-architecture-and-archunit.md).

---

## Reusable Asset Templates

- `assets/templates/DemoArchUnitTest.java`: Ready-to-use ArchUnit test suite asserting layered isolation, blocking controller-to-repository bypass, and checking naming conventions.

---

## Quick Reference Commands

| Task | Command |
| :--- | :--- |
| **Run ArchUnit test only** | `./mvnw test -Dtest=*ArchUnit*` |
| **Run all tests** | `./mvnw clean test` |
| **Run Spring Boot app** | `./mvnw spring-boot:run` |
