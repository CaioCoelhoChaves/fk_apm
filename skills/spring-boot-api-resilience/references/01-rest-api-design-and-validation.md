# 05 - REST API Design & Error Handling (RFC 7807)

## Table of Contents
- [1. Richardson Maturity Model & HTTP Semantics](#1-richardson-maturity-model--http-semantics)
- [2. Request & Response DTOs using Java Records](#2-request--response-dtos-using-java-records)
- [3. Jakarta Bean Validation](#3-jakarta-bean-validation)
- [4. RFC 7807: Problem Details for HTTP APIs](#4-rfc-7807-problem-details-for-http-apis)
- [5. Canonical Global Exception Handler](#5-canonical-global-exception-handler)
- [6. Pagination Headers & CORS Configuration](#6-pagination-headers--cors-configuration)

---

## 1. Richardson Maturity Model & HTTP Semantics

Enterprise Spring Boot APIs must reach at least **Level 2** (HTTP Verbs & Status Codes):
- **Level 0**: The Swamp of POX (single URI, POST for everything, e.g. SOAP/XML-RPC).
- **Level 1**: Resources (distinct URIs per resource: `/pacotes`, `/clientes`).
- **Level 2**: HTTP Verbs & Status Codes:
  - `GET`: Safe, idempotent retrieval. Return `200 OK` or `404 Not Found`.
  - `POST`: Non-idempotent creation. Return `201 Created` with `Location` header.
  - `PUT`: Idempotent full replacement. Return `200 OK` or `204 No Content`.
  - `PATCH`: Partial update. Return `200 OK`.
  - `DELETE`: Idempotent removal. Return `204 No Content` (even if resource was already removed).
- **Level 3**: Hypermedia Controls (HATEOAS).

---

## 2. Request & Response DTOs using Java Records

### Why Never Expose JPA Entities Directly in REST Endpoints
- **Leaky Abstraction**: Database schemas leak directly to clients.
- **Serialization Failures**: Infinite loops during Jackson serialization with bidirectional relationships (`@OneToMany`/`@ManyToOne`).
- **Security Flaws (Over-posting)**: Malicious clients can send internal fields (e.g. `isAdmin: true` or `balance: 999999`).
- **Versioning**: Changing entity columns breaks public API consumers.

### The Standard: Java 16+ `record`s for DTOs
```java
public record PacoteRequest(
    @NotBlank(message = "Descrição é obrigatória")
    @Size(min = 3, max = 255, message = "Descrição deve ter entre 3 e 255 caracteres")
    String descricao,

    @NotNull(message = "ID da localidade é obrigatório")
    UUID localidadeId
) {}

public record PacoteResponse(
    UUID id,
    String descricao,
    String localidade,
    double valorTotal,
    List<ItemPacoteResponse> itens
) {}
```

---

## 3. Jakarta Bean Validation

Spring Boot validates request bodies when annotated with `@Valid`:

```java
@PostMapping("/pacotes")
public ResponseEntity<PacoteResponse> criar(
        @Valid @RequestBody PacoteRequest request,
        UriComponentsBuilder uriBuilder) {

    PacoteResponse criado = pacoteService.criar(request);
    URI location = uriBuilder.path("/pacotes/{id}").buildAndExpand(criado.id()).toUri();
    return ResponseEntity.created(location).body(criado);
}
```

### Common Annotations
- `@NotNull`, `@NotBlank`, `@NotEmpty`
- `@Size(min = ..., max = ...)`
- `@Min(...)`, `@Max(...)`, `@Positive`, `@PositiveOrZero`
- `@Pattern(regexp = "^[A-Za-z0-9]+$", message = "Somente caracteres alfanuméricos")`
- `@Email`

---

## 4. RFC 7807: Problem Details for HTTP APIs

RFC 7807 defines standard error responses with `Content-Type: application/problem+json`:
- `type`: URI identifying the problem type.
- `title`: Short human-readable summary.
- `status`: HTTP status code matching the response.
- `detail`: Detailed explanation specific to this occurrence.
- `instance`: URI of the request that caused the error.

Spring Boot 3 natively supports RFC 7807 via `ProblemDetail` and `ResponseEntityExceptionHandler`.

---

## 5. Canonical Global Exception Handler

```java
package br.com.empresa.rental.config;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.net.URI;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidationExceptions(MethodArgumentNotValidException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, "A requisição possui parâmetros inválidos."
        );
        problem.setType(URI.create("https://api.empresa.com.br/errors/validation-error"));
        problem.setTitle("Erro de Validação");
        problem.setProperty("timestamp", Instant.now());

        Map<String, String> fieldErrors = new HashMap<>();
        for (FieldError fe : ex.getBindingResult().getFieldErrors()) {
            fieldErrors.put(fe.getField(), fe.getDefaultMessage());
        }
        problem.setProperty("invalidParams", fieldErrors);

        return problem;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ProblemDetail handleIllegalArgument(IllegalArgumentException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.getMessage());
        problem.setType(URI.create("https://api.empresa.com.br/errors/bad-request"));
        problem.setTitle("Parâmetro Inválido");
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGeneralException(Exception ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "Ocorreu um erro interno inesperado."
        );
        problem.setType(URI.create("https://api.empresa.com.br/errors/internal-error"));
        problem.setTitle("Erro Interno");
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }
}
```

---

## 6. Pagination Headers & CORS Configuration

### Custom Pagination Headers
Expose total item count via `X-Total-Count`:
```java
@GetMapping("/pacotes")
public ResponseEntity<List<PacoteResponse>> listar(Pageable pageable) {
    Page<PacoteResponse> page = pacoteService.listar(pageable);
    return ResponseEntity.ok()
            .header("X-Total-Count", String.valueOf(page.getTotalElements()))
            .header("Access-Control-Expose-Headers", "X-Total-Count")
            .body(page.getContent());
}
```

### Global CORS Configuration
```java
package br.com.empresa.rental.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("http://localhost:3000", "https://app.empresa.com.br")
                .allowedMethods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .exposedHeaders("X-Total-Count")
                .allowCredentials(true);
    }
}
```
