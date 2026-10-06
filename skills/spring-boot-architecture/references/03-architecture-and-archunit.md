# 03 - Architecture & ArchUnit Governance

## Table of Contents
- [1. Layered Architecture Principles](#1-layered-architecture-principles)
- [2. Dependency Injection: Strict Constructor Injection](#2-dependency-injection-strict-constructor-injection)
- [3. Conditional Beans & Polymorphic Profiles](#3-conditional-beans--polymorphic-profiles)
- [4. ArchUnit: Architecture as Code](#4-archunit-architecture-as-code)
- [5. Canonical ArchUnit Test Suite](#5-canonical-archunit-test-suite)

---

## 1. Layered Architecture Principles

In enterprise Spring applications, maintain strict unidirectional dependencies between layers:

```
[ Controller / REST Layer ]
         │ (calls)
         ▼
[ Service / Use Case Layer ]
         │ (calls)
         ▼
[ Repository / Persistence Layer ]
         │ (loads & stores)
         ▼
[ Domain Entities / Value Objects ]
```

### Strict Rules of Engagement
1. **Controllers** must NEVER access Repositories directly. All operations pass through Services.
2. **Services** contain orchestration and business rules; they interact with Repositories and Domain Entities.
3. **Repositories** contain only data retrieval and persistence logic; they must never call Services or Controllers.
4. **Domain** contains business invariants and is independent of web or presentation concerns.

---

## 2. Dependency Injection: Strict Constructor Injection

### The Anti-Pattern: Field Injection (`@Autowired`)
```java
// ANTI-PATTERN: Field injection
@RestController
public class PacoteController {
    @Autowired
    private PacoteService service; // Violates encapsulation, hides dependencies, breaks pure unit testing
}
```
*Why field injection is prohibited:*
- **Not Testable**: You cannot instantiate the class in a plain JUnit test without Spring reflection or Mockito annotations.
- **Mutable**: Dependencies cannot be declared `final`, making beans prone to mutation.
- **Hides Complexity**: Easy to accumulate 10+ dependencies without noticing a Single Responsibility Principle (SRP) violation.

### The Standard: Constructor Injection with `final` Fields
Spring Boot automatically injects constructor arguments when a single constructor exists (no `@Autowired` required).

```java
// RECOMMENDED: Explicit, immutable, testable constructor injection
@RestController
public class PacoteController {

    private final PacoteService pacoteService;

    public PacoteController(PacoteService pacoteService) {
        this.pacoteService = Objects.requireNonNull(pacoteService, "PacoteService is required");
    }
}
```

---

## 3. Conditional Beans & Polymorphic Profiles

Decouple implementations using Spring's conditional loading annotations:

### `@ConditionalOnProperty`
Allows swapping implementations via `application.properties` (e.g. dummy in-memory vs real JPA repository, mock payment gateway vs production gateway):

```java
@Repository
@ConditionalOnProperty(
    name = "app.repository.type",
    havingValue = "dummy",
    matchIfMissing = false
)
public class DummyPacoteRepository implements PacoteRepository { ... }

@Repository
@ConditionalOnProperty(
    name = "app.repository.type",
    havingValue = "jpa",
    matchIfMissing = true
)
public class JpaPacoteRepositoryAdapter implements PacoteRepository { ... }
```

---

## 4. ArchUnit: Architecture as Code

**ArchUnit** is a Java testing library that checks architecture rules by analyzing compiled bytecode. It runs inside standard JUnit 5 test suites and prevents architectural rot during CI/CD.

### Key Governance Capabilities
- Ensure Controllers are not called by other layers.
- Ensure Services are only called by Controllers and Services.
- Ensure Repositories are only accessed by Services.
- Ensure Entities do not depend on Spring MVC or Controller annotations.
- Ensure naming conventions (e.g. classes in `..controller..` must be named `*Controller`).

---

## 5. Canonical ArchUnit Test Suite

Place this test in `src/test/java/.../ApplicationArchUnitTest.java`:

```java
package br.com.empresa.rental;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.library.Architectures;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.Architectures.layeredArchitecture;

public class ApplicationArchUnitTest {

    private static JavaClasses importedClasses;

    @BeforeAll
    public static void setup() {
        importedClasses = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .importPackages("br.com.empresa.rental");
    }

    @Test
    @DisplayName("Garantir isolamento estrito de camadas arquiteturais")
    public void ensureLayerDependencies() {
        Architectures.LayeredArchitecture arch = layeredArchitecture()
                .consideringAllDependencies()
                .layer("Controller").definedBy("..controller..")
                .layer("Service").definedBy("..service..")
                .layer("Persistence").definedBy("..repository..")
                .layer("Domain").definedBy("..domain..")

                // Constraints
                .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
                .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller", "Service")
                .whereLayer("Persistence").mayOnlyBeAccessedByLayers("Service");

        arch.check(importedClasses);
    }

    @Test
    @DisplayName("Controllers não devem acessar Repositories diretamente")
    public void controllersMustNotAccessRepositoriesDirectly() {
        noClasses().that().resideInAPackage("..controller..")
                .should().dependOnClassesThat().resideInAPackage("..repository..")
                .because("A camada de controle deve sempre passar pela camada de serviço")
                .check(importedClasses);
    }

    @Test
    @DisplayName("Convenção de nomenclatura para Controllers e Services")
    public void namingConventionsMustBeRespected() {
        classes().that().resideInAPackage("..controller..")
                .should().haveSimpleNameEndingWith("Controller")
                .check(importedClasses);

        classes().that().resideInAPackage("..service..")
                .should().haveSimpleNameEndingWith("Service")
                .check(importedClasses);
    }
}
```
