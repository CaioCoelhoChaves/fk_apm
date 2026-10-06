# 06 - Resilience & Distributed Systems Patterns

## Table of Contents
- [1. Fallacies of Distributed Computing & Leaky Abstractions](#1-fallacies-of-distributed-computing--leaky-abstractions)
- [2. The Reality: APIs Do NOT Propagate ACID Transactions](#2-the-reality-apis-do-not-propagate-acid-transactions)
- [3. Idempotency Pattern (X-Idempotency-Id)](#3-idempotency-pattern-x-idempotency-id)
- [4. Spring Retry for Concurrent Collisions](#4-spring-retry-for-concurrent-collisions)
- [5. Commutativity & Out-of-Order Execution](#5-commutativity--out-of-order-execution)
- [6. Saga Pattern & Compensating Actions](#6-saga-pattern--compensating-actions)
- [7. The Watchdog Pattern](#7-the-watchdog-pattern)

---

## 1. Fallacies of Distributed Computing & Leaky Abstractions

Whenever a Spring Boot application communicates over a network (HTTP, REST, Message Queues), it is subject to the **8 Fallacies of Distributed Computing** (Peter Deutsch):
1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. Topology doesn't change.
6. There is one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

**Joel Spolsky's Law of Leaky Abstractions:**
> *"All non-trivial abstractions, to some degree, are leaky."*
HTTP abstraction layers, database drivers, and ORMs leak underlying network timeouts, duplicate packets, and disconnection failures into application code.

---

## 2. The Reality: APIs Do NOT Propagate ACID Transactions

When Service A calls Service B via REST, a database `@Transactional` in Service A **cannot** span across the HTTP call to Service B.
If Service A throws an exception after Service B completed its step, Service B's changes are already committed. We must design for **Eventual Consistency** using Idempotency, Commutativity, Sagas, and Watchdogs.

---

## 3. Idempotency Pattern (X-Idempotency-Id)

An operation is **idempotent** if applying it multiple times produces the exact same outcome as applying it once: $f(f(x)) = f(x)$.

### Implementation Strategy
1. Client generates a unique transaction UUID (`X-Idempotency-Id`) in the HTTP request header.
2. The backend stores `tx_id` with a **Unique Constraint** in the database.
3. If a network timeout occurs and the client retries, the backend detects the duplicate `tx_id` and returns the existing resource without performing duplicate operations (such as double charging a credit card).

#### Controller Layer
```java
@PostMapping("/contratacoes")
public ResponseEntity<ContratacaoResponse> contratar(
        @RequestHeader("X-Idempotency-Id") String txId,
        @Valid @RequestBody ContratacaoRequest request) {

    Contratacao contratacao = contratacaoService.criar(request, txId);
    return ResponseEntity.ok(ContratacaoResponse.from(contratacao));
}
```

#### Service Layer with Unique Constraint & Query-First Pattern
```java
@Service
public class ContratacaoService {

    private final ContratacaoRepository repository;

    @Transactional
    public Contratacao criar(ContratacaoRequest req, String txId) {
        // A priori check
        Optional<Contratacao> existente = repository.findByTxId(txId);
        if (existente.isPresent()) {
            return existente.get();
        }

        Contratacao nova = new Contratacao(req.clienteId(), req.pacoteId(), txId);
        return repository.save(nova);
    }
}
```

---

## 4. Spring Retry for Concurrent Collisions

When two concurrent requests arrive simultaneously with the same `X-Idempotency-Id` (a posteriori race condition), both pass the initial `findByTxId` check. The database Unique Constraint triggers a `DataIntegrityViolationException`.

Use **Spring Retry** to automatically retry and fetch the record committed by the winning thread:

```java
@Service
public class ContratacaoService {

    private final ContratacaoRepository repository;

    @Retryable(
        retryFor = DataIntegrityViolationException.class,
        maxAttemptsExpression = "${app.retry.max-attempts:3}",
        backoff = @Backoff(delay = 100, multiplier = 2.0)
    )
    @Transactional
    public Contratacao criarComRetry(ContratacaoRequest req, String txId) {
        Optional<Contratacao> existente = repository.findByTxId(txId);
        if (existente.isPresent()) {
            return existente.get();
        }

        Contratacao nova = new Contratacao(req.clienteId(), req.pacoteId(), txId);
        return repository.save(nova);
    }
}
```

---

## 5. Commutativity & Out-of-Order Execution

In distributed networks, operations can arrive out of order:
- A user clicks "Cancel Payment", sending a `DELETE /pagamentos/{id}`.
- Because of latency, the earlier `POST /pagamentos` is still in flight, so `DELETE` arrives **first**.

### Rules for Commutativity
1. **Idempotent DELETE**: A `DELETE` must return `204 No Content` even if the target resource does not yet exist.
2. **Cancellation Intent / Tombstone**: When a cancellation arrives for an unknown transaction, record a tombstone in a `cancelamentos_pendentes` table. When the late `POST` finally arrives, check the tombstone table and abort creation or mark it as immediately cancelled.

---

## 6. Saga Pattern & Compensating Actions

A **Saga** is a sequence of local transactions where each step updates a local database and publishes a message or triggers the next step.

### Compensating Actions
If Step 3 fails, the saga must execute **compensating actions** in reverse order:
1. `ReserveHotel` -> Compensator: `CancelHotelReservation`
2. `BookFlight` -> Compensator: `CancelFlightBooking`
3. `ProcessPayment` -> (Fails)

---

## 7. The Watchdog Pattern

Even with retries and compensations, processes can crash midway (power outage, kill -9, network partition). The **Watchdog Pattern** ensures self-healing consistency.

### How It Works
1. **Control Table**: Before making an external remote call, record an entry in `saga_control` with state `PENDING` and a timestamp.
2. When the call succeeds, update state to `COMPLETED`.
3. **Watchdog Job**: A scheduled background task runs periodically (e.g. every 60 seconds).
4. Any saga that remains in `PENDING` state for longer than the timeout threshold (e.g. 5 minutes) is considered orphaned.
5. The watchdog executes compensating actions for completed steps and marks the transaction as `COMPENSATED`.

```java
@Component
public class SagaWatchdog {

    private final SagaControlRepository repository;
    private final PaymentCompensator compensator;

    @Scheduled(fixedDelay = 60000)
    public void reconciliarTransacoesPendentes() {
        Instant threshold = Instant.now().minus(Duration.ofMinutes(5));
        List<SagaControl> pendentes = repository.findByStatusAndTimestampBefore(
                SagaStatus.PENDING, threshold
        );

        for (SagaControl saga : pendentes) {
            try {
                compensator.compensar(saga);
                saga.setStatus(SagaStatus.COMPENSATED);
                repository.save(saga);
            } catch (Exception ex) {
                // Log and alert SRE
            }
        }
    }
}
```
