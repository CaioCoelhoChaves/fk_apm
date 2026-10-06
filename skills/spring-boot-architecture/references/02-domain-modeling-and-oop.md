# 02 - Domain Modeling & Object-Oriented Principles

## Table of Contents
- [1. Combating the Anemic Domain Model](#1-combating-the-anemic-domain-model)
- [2. Defensive Programming & Encapsulation](#2-defensive-programming--encapsulation)
- [3. Invariants & Business Logic Inside Entities](#3-invariants--business-logic-inside-entities)
- [4. Rich Enums & State Management](#4-rich-enums--state-management)
- [5. Polymorphism Over Conditional Cascades](#5-polymorphism-over-conditional-cascades)
- [6. Canonical Example: Rich Domain Entity](#6-canonical-example-rich-domain-entity)

---

## 1. Combating the Anemic Domain Model

An **Anemic Domain Model** (Martin Fowler) is an anti-pattern where domain classes are reduced to pure data structures with getters and setters, while all business rules, calculations, and state transitions are scattered across external procedural service classes.

### The Problem (Anemic Model Anti-Pattern)
```java
// ANTI-PATTERN: Dumb data bag
public class Pedido {
    private List<ItemPedido> itens;
    private double valorTotal;
    private String status;

    public List<ItemPedido> getItens() { return itens; }
    public void setItens(List<ItemPedido> itens) { this.itens = itens; }
    public double getValorTotal() { return valorTotal; }
    public void setValorTotal(double valorTotal) { this.valorTotal = valorTotal; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
```
*Why this fails:*
- Anyone can call `pedido.getItens().clear()` or `pedido.setValorTotal(-500.0)`.
- Internal invariants cannot be enforced.
- Business rules are duplicated across services.

### The Solution (Rich Domain Model)
Entities must encapsulate state and the operations that mutate that state. Invariants are checked at mutation boundaries.

```java
// RECOMMENDED: Rich Domain Model
public class Pedido {
    private final List<ItemPedido> itens = new ArrayList<>();
    private StatusPedido status = StatusPedido.CRIADO;

    public void adicionarItem(ItemPedido item) {
        Objects.requireNonNull(item, "Item não pode ser nulo");
        if (this.status != StatusPedido.CRIADO) {
            throw new IllegalStateException("Não é permitido adicionar itens a pedidos já finalizados.");
        }
        this.itens.add(item);
    }

    public List<ItemPedido> getItens() {
        return Collections.unmodifiableList(this.itens);
    }

    public double getValorTotal() {
        return this.itens.stream()
                .mapToDouble(ItemPedido::getPreco)
                .sum();
    }
}
```

---

## 2. Defensive Programming & Encapsulation

### Rule 1: Never Return Direct References to Mutable Collections
Direct collection access allows external code to mutate entity state without triggering domain events, validations, or dirty-checking rules:
```java
// BAD: Caller can do entity.getItems().add(null) or entity.getItems().clear()
public List<Item> getItems() {
    return this.items;
}

// GOOD: Unmodifiable view protects the internal collection
public List<Item> getItems() {
    return Collections.unmodifiableList(this.items);
}
```

### Rule 2: Defensive Copies on Inputs
When accepting mutable objects (like dates, arrays, or collections), create a defensive copy or validate defensively:
```java
public void atualizarItens(List<Item> novosItens) {
    if (novosItens == null) {
        this.items.clear();
    } else {
        this.items.clear();
        this.items.addAll(novosItens);
    }
}
```

---

## 3. Invariants & Business Logic Inside Entities

Business methods must reflect real-world ubiquitous language (DDD) rather than technical setters:
- Prefer `cliente.contratar(pacote)` over `contratacao.setCliente(cliente); contratacao.setPacote(pacote);`
- Prefer `conta.sacar(valor)` over `conta.setSaldo(conta.getSaldo() - valor)`
- Prefer `aluguel.finalizar(dataDevolucao)` over external procedural recalculations.

---

## 4. Rich Enums & State Management

In Java, enums are full-featured classes that can encapsulate behavior, constants, and custom logic.

### JPA Persistence Rule
**Always** use `@Enumerated(EnumType.STRING)`. Never use `EnumType.ORDINAL` because reordering or adding enum constants corrupts database references.

```java
@Enumerated(EnumType.STRING)
@Column(name = "STATUS", nullable = false, length = 30)
private StatusAluguel status;
```

### Rich Enum with Behavior & Abstract Methods
Enums can define polymorphic behavior per constant, eliminating messy `switch` or `if-else` ladders:

```java
public enum StatusAluguel {
    SOLICITADO {
        @Override
        public boolean podeTransicionarPara(StatusAluguel proximo) {
            return proximo == APROVADO || proximo == CANCELADO;
        }
    },
    APROVADO {
        @Override
        public boolean podeTransicionarPara(StatusAluguel proximo) {
            return proximo == EM_ANDAMENTO || proximo == CANCELADO;
        }
    },
    EM_ANDAMENTO {
        @Override
        public boolean podeTransicionarPara(StatusAluguel proximo) {
            return proximo == FINALIZADO;
        }
    },
    FINALIZADO {
        @Override
        public boolean podeTransicionarPara(StatusAluguel proximo) {
            return false;
        }
    },
    CANCELADO {
        @Override
        public boolean podeTransicionarPara(StatusAluguel proximo) {
            return false;
        }
    };

    public abstract boolean podeTransicionarPara(StatusAluguel proximo);
}
```

---

## 5. Polymorphism Over Conditional Cascades

Replace `if (tipo == "HOTEL") ... else if (tipo == "VOO")` with object-oriented polymorphism:
- Define an abstract base class or interface.
- Subclasses implement specific rules (e.g. calculation of daily rates, mileage, baggage allowances).
- Combine with JPA `@Inheritance(strategy = InheritanceType.JOINED)` and Jackson polymorphic deserialization (`@JsonTypeInfo`, `@JsonSubTypes`).

---

## 6. Canonical Example: Rich Domain Entity

```java
package br.com.empresa.rental.domain;

import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;

import java.sql.Types;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(name = "CLIENTES")
public class Cliente {

    @Id
    @Column(name = "ID")
    @JdbcTypeCode(Types.VARCHAR)
    @GeneratedValue(generator = "ulid_generator")
    private UUID id;

    @Column(name = "NOME", nullable = false, length = 120)
    private String nome;

    @Column(name = "DATA_NASCIMENTO", nullable = false)
    private LocalDate dataNascimento;

    @OneToMany(mappedBy = "cliente", cascade = CascadeType.ALL, orphanRemoval = true)
    private final List<Contratacao> contratacoes = new ArrayList<>();

    protected Cliente() {
        // Required by JPA
    }

    public Cliente(String nome, LocalDate dataNascimento) {
        this.nome = Objects.requireNonNull(nome, "Nome é obrigatório");
        this.dataNascimento = Objects.requireNonNull(dataNascimento, "Data de nascimento é obrigatória");
    }

    public Contratacao contratar(Pacote pacote) {
        Objects.requireNonNull(pacote, "Pacote não pode ser nulo");
        Contratacao nova = new Contratacao(this, pacote);
        this.contratacoes.add(nova);
        return nova;
    }

    public UUID getId() { return id; }
    public String getNome() { return nome; }
    public LocalDate getDataNascimento() { return dataNascimento; }

    public List<Contratacao> getContratacoes() {
        return Collections.unmodifiableList(contratacoes);
    }
}
```
