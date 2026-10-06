# 07 - Database Migrations with Liquibase

## Table of Contents
- [1. Overview & Golden Rules](#1-overview--golden-rules)
- [2. Spring Boot Setup](#2-spring-boot-setup)
- [3. Changeset Design Principles](#3-changeset-design-principles)
- [4. Master Changelog Structure](#4-master-changelog-structure)
- [5. Canonical Changeset Examples](#5-canonical-changeset-examples)
- [6. Rollbacks & Multi-DBMS Support](#6-rollbacks--multi-dbms-support)

---

## 1. Overview & Golden Rules

In production Spring Boot applications:
- **`spring.jpa.hibernate.ddl-auto` must NEVER be `create`, `create-drop`, or `update`**. Set it to `validate` or `none`.
- All database schema modifications, indexes, foreign keys, and seeds must be tracked in version control through database migrations (Liquibase or Flyway).

### Why Liquibase?
- **Multi-DBMS portability**: Declarative XML/YAML changesets translate automatically to PostgreSQL, MySQL, Oracle, H2, and SQL Server.
- **Auditing**: Records executed changesets in `DATABASECHANGELOG` and lock status in `DATABASECHANGELOGLOCK`.
- **Automated Rollbacks**: Supports reverse operations (`<rollback>`).

---

## 2. Spring Boot Setup

### Maven Dependency
```xml
<dependency>
    <groupId>org.liquibase</groupId>
    <artifactId>liquibase-core</artifactId>
</dependency>
```

### Application Properties
```properties
spring.liquibase.enabled=true
spring.liquibase.change-log=classpath:db/changelog/db.changelog-master.xml
spring.jpa.hibernate.ddl-auto=validate
```

---

## 3. Changeset Design Principles

1. **One Concept Per Changeset**: Never combine multiple table creations or disparate index creations into a single changeset.
2. **Deterministic Changeset IDs**: Use the author name + UTC timestamp format (`YYYYMMDDHHmmss`) to avoid merge conflicts across distributed engineering teams:
   `id="20261006120000" author="caio"`
3. **Foreign Keys & Indices**: Always add explicit indexes to foreign key columns (`column_id`) to prevent table full scans on joins and deletes.

---

## 4. Master Changelog Structure

Organize changelogs inside `src/main/resources/db/changelog/`:
```
src/main/resources/db/changelog/
├── db.changelog-master.xml
└── changes/
    ├── 20261006100000-create-clientes.xml
    ├── 20261006100500-create-pacotes.xml
    └── 20261006101000-create-contratacoes.xml
```

Master changelog inclusion pattern:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.1.xsd">

    <include file="db/changelog/changes/20261006100000-create-clientes.xml"/>
    <include file="db/changelog/changes/20261006100500-create-pacotes.xml"/>
</databaseChangeLog>
```

---

## 5. Canonical Changeset Examples

### Table with Monotonic ULID / UUID Primary Key
```xml
<changeSet author="caio" id="20261006100000">
    <createTable tableName="clientes">
        <column name="id" type="CHAR(36)">
            <constraints nullable="false" primaryKey="true" primaryKeyName="clientes_pk"/>
        </column>
        <column name="nome" type="VARCHAR(120)">
            <constraints nullable="false"/>
        </column>
        <column name="data_nascimento" type="DATE">
            <constraints nullable="false"/>
        </column>
        <column name="created_at" type="TIMESTAMP" defaultValueComputed="CURRENT_TIMESTAMP">
            <constraints nullable="false"/>
        </column>
    </createTable>
    <rollback>
        <dropTable tableName="clientes"/>
    </rollback>
</changeSet>
```

### Table with Foreign Key and Dedicated Index
```xml
<changeSet author="caio" id="20261006101000">
    <createTable tableName="contratacoes">
        <column name="id" type="CHAR(36)">
            <constraints nullable="false" primaryKey="true" primaryKeyName="contratacoes_pk"/>
        </column>
        <column name="tx_id" type="VARCHAR(64)">
            <constraints nullable="false" unique="true" uniqueConstraintName="contratacoes_tx_id_uk"/>
        </column>
        <column name="cliente_id" type="CHAR(36)">
            <constraints nullable="false"
                         referencedTableName="clientes"
                         referencedColumnNames="id"
                         foreignKeyName="contratacoes_clientes_fk"/>
        </column>
        <column name="pacote_id" type="CHAR(36)">
            <constraints nullable="false"
                         referencedTableName="pacotes"
                         referencedColumnNames="id"
                         foreignKeyName="contratacoes_pacotes_fk"/>
        </column>
        <column name="valor" type="NUMBER(18, 2)">
            <constraints nullable="false"/>
        </column>
        <column name="data_contratacao" type="TIMESTAMP">
            <constraints nullable="false"/>
        </column>
    </createTable>

    <!-- Essential Index on Foreign Keys -->
    <createIndex tableName="contratacoes" indexName="contratacoes_cliente_idx">
        <column name="cliente_id"/>
    </createIndex>
    <createIndex tableName="contratacoes" indexName="contratacoes_pacote_idx">
        <column name="pacote_id"/>
    </createIndex>

    <rollback>
        <dropTable tableName="contratacoes"/>
    </rollback>
</changeSet>
```

---

## 6. Rollbacks & Multi-DBMS Support

Always specify `<rollback>` blocks so CI/CD pipelines can revert failed deployments automatically via `mvn liquibase:rollback`.
By using generic types like `CHAR(36)`, `VARCHAR(255)`, `NUMBER(18, 2)`, and `TIMESTAMP`, Liquibase automatically translates types cleanly across H2 (in-memory test), PostgreSQL, and Oracle (enterprise production).
