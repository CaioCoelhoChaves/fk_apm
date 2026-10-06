---
name: spring-boot-persistence
description: High-performance persistence, database migrations, and query optimization for Spring Data JPA and Hibernate 6 in Spring Boot 3.x+. Use this skill when configuring database entities and repositories, tuning JPA performance (preventing N+1 queries, two-phase pagination findIds + findAllById to avoid HHH000104 in-memory pagination warnings), configuring sequential Monotonic ULID primary keys to avoid B+Tree index page fragmentation, managing declarative transactions (@Transactional readOnly = true), or writing versioned Liquibase/Flyway database migrations with proper indexing on foreign keys.
allowed-tools: Read,Glob,Grep,Write,Edit,Bash
---

# Spring Boot Persistence & Data Performance

A dedicated guide and operational blueprint for enterprise persistence using **Spring Data JPA**, **Hibernate 6**, and **Liquibase** in **Spring Boot 3.x+**.

Focuses on relational database performance, clustered B+Tree index health, safe pagination patterns, and deterministic database migrations.

---

## Core Non-Negotiable Standards

1. **Clustered B+Tree Index Optimization (Monotonic ULID)**:
   - Random UUID v4 causes severe B+Tree leaf-node page splits, fragmentation, and random disk I/O under high write volumes.
   - Use sequential **Monotonic ULID** primary keys (`com.github.f4b6a3:ulid-creator`) stored in standard 16-byte UUID / `CHAR(36)` columns with custom Hibernate `IdentifierGenerator` supporting JDBC batch inserts.
   - See [references/01-persistence-spring-data-jpa.md](references/01-persistence-spring-data-jpa.md).

2. **High-Performance Two-Phase Pagination**:
   - Never combine `join fetch` on `@OneToMany` collections with `Pageable` in a single query. It triggers Hibernate warning `HHH000104` ("firstResult/maxResults specified with collection fetch; applying in memory!") and loads entire tables into JVM memory.
   - Implement the **Two-Phase Query Pattern**:
     1. Paginate IDs at the database index level (`Page<UUID> findIds(Pageable pageable)`).
     2. Batch fetch entities and child collections with `join fetch` using `findAllById(ids)`.
     3. Assemble into a `PageImpl<>(entities, idsPage.getPageable(), idsPage.getTotalElements())`.

3. **Declarative Transaction Boundaries**:
   - Apply `@Transactional` at the **Service layer**, never at Controllers or Repositories.
   - Always annotate read operations with `@Transactional(readOnly = true)` to disable Hibernate dirty-checking snapshots, reducing heap allocation and CPU overhead.
   - For operations that can throw checked exceptions, declare `@Transactional(rollbackFor = Exception.class)`.

4. **Versioned Database Migrations (Liquibase)**:
   - `spring.jpa.hibernate.ddl-auto` must be set to `validate` (or `none`) in production. Never use `update` or `create-drop`.
   - Manage all schema mutations through atomic Liquibase changesets identified by UTC timestamps (`YYYYMMDDHHmmss-<description>.xml`).
   - Every foreign key constraint must have a corresponding index to avoid table-level locks during cascade operations.
   - See [references/02-database-migrations-liquibase.md](references/02-database-migrations-liquibase.md).

---

## Step-by-Step Workflow

### Step 1: Sequential Primary Keys Setup (ULID)
1. Add `ulid-creator` dependency to `pom.xml`:
   ```xml
   <dependency>
       <groupId>com.github.f4b6a3</groupId>
       <artifactId>ulid-creator</artifactId>
       <version>5.2.0</version>
   </dependency>
   ```
2. Copy `UlidGenerator.java` and `package-info.java` from `assets/templates/` to your domain package.
3. Annotate entity primary keys:
   ```java
   @Id
   @GeneratedValue(generator = "ulid_generator")
   @Column(columnDefinition = "uuid", updatable = false, nullable = false)
   private UUID id;
   ```

### Step 2: Query Optimization & Two-Phase Pagination
1. Identify queries that fetch `@OneToMany` or `@ManyToMany` child collections alongside pagination.
2. In the Repository, declare two distinct queries:
   ```java
   @Query("select p.id from Pacote p")
   Page<UUID> findIds(Pageable pageable);

   @Query("select p from Pacote p join fetch p.itens where p.id in :ids")
   List<Pacote> findAllWithItensByIdIn(@Param("ids") List<UUID> ids);
   ```
3. In the Service, combine them:
   ```java
   @Transactional(readOnly = true)
   public Page<Pacote> listarPaginado(Pageable pageable) {
       Page<UUID> idsPage = pacoteRepository.findIds(pageable);
       if (idsPage.isEmpty()) {
           return Page.empty(pageable);
       }
       List<Pacote> entities = pacoteRepository.findAllWithItensByIdIn(idsPage.getContent());
       return new PageImpl<>(entities, pageable, idsPage.getTotalElements());
   }
   ```

### Step 3: Database Migrations with Liquibase
1. Ensure `db.changelog-master.xml` exists in `src/main/resources/db/changelog/`.
2. Create dedicated changeset XML files using UTC timestamp prefix:
   `src/main/resources/db/changelog/changes/20261006120000-create-pacotes.xml`.
3. Include foreign key indexes explicitly:
   ```xml
   <createIndex indexName="idx_item_pacote_id" tableName="tb_item">
       <column name="pacote_id"/>
   </createIndex>
   ```
4. Consult [references/02-database-migrations-liquibase.md](references/02-database-migrations-liquibase.md).

---

## Reusable Asset Templates

- `assets/templates/UlidGenerator.java`: Custom Hibernate `IdentifierGenerator` producing sequential ULIDs and enabling JDBC batch inserts.
- `assets/templates/package-info.java`: Package-level Hibernate `@GenericGenerator` definition.
- `assets/templates/db.changelog-master.xml`: Standard master changelog configuration.

---

## Quick Reference Commands

| Task | Command |
| :--- | :--- |
| **Validate Liquibase changesets** | `./mvnw liquibase:status` |
| **Run persistence slice tests** | `./mvnw test -Dtest=*RepositoryTest` |
| **Verify Hibernate DDL schema** | `./mvnw test-compile` |
