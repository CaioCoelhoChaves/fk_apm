# 04 - Persistence & Performance (Spring Data JPA)

## Table of Contents
- [1. Entity Lifecycle & Dirty Checking](#1-entity-lifecycle--dirty-checking)
- [2. Declarative Transaction Management (@Transactional)](#2-declarative-transaction-management-transactional)
- [3. Primary Keys & B+Tree Indexes: Monotonic ULID vs Random UUID](#3-primary-keys--btree-indexes-monotonic-ulid-vs-random-uuid)
- [4. Inheritance Mapping Strategies](#4-inheritance-mapping-strategies)
- [5. The N+1 Query Problem & In-Memory Pagination Pitfall](#5-the-n1-query-problem--in-memory-pagination-pitfall)
- [6. High-Performance Two-Phase Pagination Pattern](#6-high-performance-two-phase-pagination-pattern)

---

## 1. Entity Lifecycle & Dirty Checking

JPA defines 4 distinct entity states:
1. **Transient (New)**: Instantiated via `new`, not associated with an `EntityManager`, no database identity.
2. **Managed (Persistent)**: Associated with an active Persistence Context. Any setter mutation triggers **Dirty Checking** and is flushed to the database automatically at commit time.
3. **Detached**: Persistence context is closed or entity was detached. Changes are not tracked unless re-attached via `merge()`.
4. **Removed**: Scheduled for deletion upon transaction commit.

> [!TIP]
> Never call `repository.save(entity)` unnecessarily on an already managed entity inside a `@Transactional` boundary; Hibernate's dirty checking will automatically execute the necessary `UPDATE` statements on transaction commit.

---

## 2. Declarative Transaction Management (@Transactional)

Apply `@Transactional` at the **Service layer**, not at the Controller or Repository:
- **Read-Only Operations**: Use `@Transactional(readOnly = true)`. This instructs Hibernate to disable dirty-checking snapshots, reducing memory consumption and CPU cycles.
- **Rollback Behavior**: By default, Spring only rolls back on **unchecked exceptions** (`RuntimeException` and `Error`). For checked exceptions, specify `@Transactional(rollbackFor = Exception.class)`.

```java
@Service
public class AluguelService {

    private final AluguelRepository repository;

    @Transactional(readOnly = true)
    public Optional<Aluguel> buscarPorId(UUID id) {
        return repository.findById(id);
    }

    @Transactional
    public Aluguel aprovar(UUID id) {
        Aluguel aluguel = repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Aluguel não encontrado: " + id));
        aluguel.aprovar();
        return aluguel; // Flushed automatically via dirty checking
    }
}
```

---

## 3. Primary Keys & B+Tree Indexes: Monotonic ULID vs Random UUID

### The Problem with Random UUIDs (UUID v4)
Relational databases (PostgreSQL, MySQL InnoDB, Oracle) index primary keys using **B+Trees**.
- A standard UUID v4 is completely random.
- Inserting random keys causes random page inserts across the leaf nodes of the B+Tree.
- This causes **B+Tree page splits**, fragmentation, excessive disk I/O, cache misses, and massive degradation during write-heavy workloads.

### The Solution: Monotonic ULID
A **ULID** (Universally Unique Lexicographically Sortable Identifier) consists of:
- **48-bit timestamp** (millisecond precision, sequential order)
- **80-bit cryptographic randomness**
- Stored efficiently in a standard 16-byte UUID / `CHAR(36)` column while maintaining strict sequential insertion order.

### Implementation Setup

#### 1. Add Dependency
```xml
<dependency>
    <groupId>com.github.f4b6a3</groupId>
    <artifactId>ulid-creator</artifactId>
    <version>5.2.0</version>
</dependency>
```

#### 2. Create Custom Hibernate Generator
```java
package br.com.empresa.rental.domain;

import com.github.f4b6a3.ulid.UlidCreator;
import org.hibernate.HibernateException;
import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.id.IdentifierGenerator;

import java.io.Serializable;
import java.util.UUID;

public class UlidGenerator implements IdentifierGenerator {

    @Override
    public Serializable generate(SharedSessionContractImplementor session, Object object) 
            throws HibernateException {
        return UlidCreator.getMonotonicUlid().toUuid();
    }

    @Override
    public boolean supportsJdbcBatchInserts() {
        return true; // Enables high-performance JDBC batching
    }
}
```

#### 3. Register Generator in `package-info.java`
```java
@GenericGenerator(
    name = "ulid_generator",
    strategy = "br.com.empresa.rental.domain.UlidGenerator"
)
package br.com.empresa.rental.domain;

import org.hibernate.annotations.GenericGenerator;
```

#### 4. Annotate Entities
```java
@Id
@Column(name = "ID")
@JdbcTypeCode(Types.VARCHAR)
@GeneratedValue(generator = "ulid_generator")
private UUID id;
```

---

## 4. Inheritance Mapping Strategies

JPA supports 3 inheritance strategies:
1. `InheritanceType.SINGLE_TABLE`: All subclasses in one wide table with a discriminator column. Fastest for queries, but allows nullable columns.
2. `InheritanceType.JOINED`: Normalized tables. Base table contains shared columns; child tables contain specific columns connected via foreign key. Best compromise between normalization and polymorphism.
3. `InheritanceType.TABLE_PER_CLASS`: Separate table per concrete class. Slow polymorphic queries with union.

### Canonical Joined Inheritance with Polymorphic Jackson DTOs
```java
@Entity
@Table(name = "ITEMS_PACOTE")
@Inheritance(strategy = InheritanceType.JOINED)
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "tipo")
@JsonSubTypes({
    @JsonSubTypes.Type(value = Hospedagem.class, name = "hotel"),
    @JsonSubTypes.Type(value = LocacaoVeiculo.class, name = "veiculo")
})
public abstract class ItemPacote {
    @Id
    @GeneratedValue(generator = "ulid_generator")
    private UUID id;

    @Column(name = "PRECO", nullable = false)
    private double preco;
}

@Entity
@Table(name = "HOTEIS")
@PrimaryKeyJoinColumn(name = "ID")
public class Hospedagem extends ItemPacote {
    @Column(name = "NOME_HOTEL", nullable = false)
    private String nomeHotel;
}
```

---

## 5. The N+1 Query Problem & In-Memory Pagination Pitfall

### The N+1 Problem
Accessing lazy collections (e.g. `pacote.getItems()`) in a loop issues 1 query to fetch the parent + N queries to fetch child collections for each row.

### The In-Memory Pagination Warning (HHH000104)
Attempting to solve N+1 by combining `join fetch` with pagination:
```java
// DANGEROUS: Causes HHH000104 warning
@Query("select p from Pacote p join fetch p.items")
Page<Pacote> findAllWithItems(Pageable pageable);
```
**Hibernate logs:**
`HHH000104: firstResult/maxResults specified with collection fetch; applying in memory!`
Hibernate loads the **ENTIRE database table** into JVM heap memory and filters pages in RAM, leading to `OutOfMemoryError`.

---

## 6. High-Performance Two-Phase Pagination Pattern

The production standard to cleanly paginate parent entities with child collections:

### Phase 1: Query IDs with Database Pagination
Query only IDs using database-level `LIMIT` / `OFFSET`:
```java
@Repository
public interface PacoteRepository extends JpaRepository<Pacote, UUID> {

    @Query("select p.id from Pacote p")
    Page<UUID> findIds(Pageable pageable);

    @Query("select p.id from Pacote p where p.descricao like :criteria or p.localidade.descricao like :criteria")
    Page<UUID> findIds(@Param("criteria") String criteria, Pageable pageable);

    @Override
    @Query("select distinct p from Pacote p join fetch p.items where p.id in :ids")
    List<Pacote> findAllById(@Param("ids") Iterable<UUID> ids);
}
```

### Phase 2: Batch Fetch Matching Entities in Service
```java
@Service
public class PacoteService {

    private final PacoteRepository repository;

    public PacoteService(PacoteRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public Page<Pacote> obterPacotes(String criteria, Pageable pageable) {
        // Step 1: Paginate primary keys at the DB index level
        Page<UUID> idsPage = (criteria == null || criteria.isBlank())
                ? repository.findIds(pageable)
                : repository.findIds("%" + criteria + "%", pageable);

        if (idsPage.isEmpty()) {
            return Page.empty(pageable);
        }

        // Step 2: Fetch full entity graphs in a single batch query by IDs
        List<Pacote> pacotes = repository.findAllById(idsPage.getContent());

        return new PageImpl<>(pacotes, idsPage.getPageable(), idsPage.getTotalElements());
    }
}
```
**Benefits:**
- Exactly 2 queries executed.
- Zero in-memory pagination warnings.
- Predictable query performance regardless of dataset size.
