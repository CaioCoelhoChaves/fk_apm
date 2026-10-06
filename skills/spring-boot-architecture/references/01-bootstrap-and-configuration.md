# 01 - Bootstrap & Configuration (Spring Boot 3.x + Java 17/21)

## Table of Contents
- [1. Overview & Modern Stack](#1-overview--modern-stack)
- [2. Bootstrapping with Spring Initializr](#2-bootstrapping-with-spring-initializr)
- [3. Essential Dependencies (Maven pom.xml)](#3-essential-dependencies-maven-pomxml)
- [4. Project Structure Standard](#4-project-structure-standard)
- [5. Application Entrypoint & Auto-Configuration](#5-application-entrypoint--auto-configuration)
- [6. Configuration Best Practices](#6-configuration-best-practices)
- [7. Spring Profiles & Environment Management](#7-spring-profiles--environment-management)

---

## 1. Overview & Modern Stack

Spring Boot 3+ builds on Spring Framework 6 and requires **Java 17 minimum** (with first-class support for Java 21 LTS virtual threads). It embraces Jakarta EE 10 specifications (replacing legacy `javax.*` packages with `jakarta.*`).

### Core Tenets
1. **Opinionated Defaults**: Sensible autoconfiguration that steps back when custom beans are supplied.
2. **Production-Ready from Day 1**: Built-in health metrics, externalized configuration, and container-friendly builds.
3. **No Code Generation / No XML required**: Prefer pure Java configuration using typed annotations.

---

## 2. Bootstrapping with Spring Initializr

When creating a new application, configure:
- **Project**: Maven (or Gradle)
- **Language**: Java
- **Spring Boot**: 3.x+
- **Packaging**: Jar
- **Java Version**: 17 or 21
- **Group**: Domain reverse notation (e.g. `br.com.empresa` or `br.com.pecepoli`)
- **Artifact / Name**: kebab-case or concise identifier (e.g. `rental-service`)

### Quick CLI Generation (curl)
```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,validation,actuator,devtools,h2 \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.2.4 \
  -d javaVersion=17 \
  -d groupId=br.com.empresa \
  -d artifactId=rental-service \
  -d name=rental-service \
  -o rental-service.zip && unzip rental-service.zip
```

---

## 3. Essential Dependencies (Maven pom.xml)

A production-grade Spring Boot backend includes the following baseline dependencies:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.4</version>
        <relativePath/>
    </parent>

    <groupId>br.com.empresa</groupId>
    <artifactId>rental-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <name>rental-service</name>
    <description>Enterprise Spring Boot Backend</description>

    <properties>
        <java.version>17</java.version>
        <ulid-creator.version>5.2.0</ulid-creator.version>
        <archunit.version>1.2.1</archunit.version>
    </properties>

    <dependencies>
        <!-- 1. Web & REST -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- 2. Bean Validation (Jakarta Validation) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- 3. Persistence (Spring Data JPA / Hibernate 6) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- 4. Monotonic ULID Generator (B+Tree friendly primary keys) -->
        <dependency>
            <groupId>com.github.f4b6a3</groupId>
            <artifactId>ulid-creator</artifactId>
            <version>${ulid-creator.version}</version>
        </dependency>

        <!-- 5. Database Migrations (Liquibase or Flyway) -->
        <dependency>
            <groupId>org.liquibase</groupId>
            <artifactId>liquibase-core</artifactId>
        </dependency>

        <!-- 6. Resilience & Retry -->
        <dependency>
            <groupId>org.springframework.retry</groupId>
            <artifactId>spring-retry</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-aspects</artifactId>
        </dependency>

        <!-- 7. Observability & Operations -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>

        <!-- 8. Developer Tools -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>

        <!-- 9. In-Memory Database for local dev / fast tests -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- 10. Test Ecosystem -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.tngtech.archunit</groupId>
            <artifactId>archunit-junit5</artifactId>
            <version>${archunit.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 4. Project Structure Standard

Organize packages cleanly by layer or by feature with strict boundaries:

```
src/
├── main/
│   ├── java/br/com/empresa/rental/
│   │   ├── Application.java               # Main entrypoint
│   │   ├── config/                        # Security, WebMvc, JpaConfig, Jackson
│   │   ├── controller/                    # REST endpoints (@RestController)
│   │   ├── dto/                           # Request & Response Records
│   │   │   ├── request/
│   │   │   └── response/
│   │   ├── domain/                        # Entities, Enums, Value Objects, Identifiers
│   │   │   ├── package-info.java          # Global Hibernate identifier generator declarations
│   │   │   └── UlidGenerator.java         # Monotonic ULID Hibernate generator
│   │   ├── repository/                    # Spring Data JPA Repositories
│   │   └── service/                       # Business logic & Transactions (@Service)
│   └── resources/
│       ├── application.properties         # Base configuration
│       ├── application-dev.properties     # Dev overrides (H2 console, debug logs)
│       ├── application-prod.properties    # Production (Hikari pool, credentials)
│       └── db/changelog/
│           └── db.changelog-master.xml    # Liquibase master migration file
└── test/
    ├── java/br/com/empresa/rental/
    │   ├── ApplicationArchUnitTest.java   # ArchUnit architectural verification
    │   ├── controller/                    # @WebMvcTest slice tests
    │   ├── service/                       # Unit tests with Mockito
    │   └── repository/                    # @DataJpaTest slice tests
    └── resources/
        └── application-test.properties    # Test configuration
```

---

## 5. Application Entrypoint & Auto-Configuration

```java
package br.com.empresa.rental;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.retry.annotation.EnableRetry;

@SpringBootApplication
@EnableRetry
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

---

## 6. Configuration Best Practices

### Prefer Type-Safe `@ConfigurationProperties` over scattered `@Value`
Instead of repeating `@Value("${app.payments.timeout}")` across multiple services, bind properties to a validated Java record or POJO.

```java
package br.com.empresa.rental.config;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

@Validated
@ConfigurationProperties(prefix = "app.rental")
public record RentalProperties(
    @NotBlank String serviceName,
    @Min(1) @Max(10) int maxRetryAttempts,
    Duration connectionTimeout
) {}
```

Register via `@ConfigurationPropertiesScan` or `@EnableConfigurationProperties(RentalProperties.class)` in a `@Configuration` class.

---

## 7. Spring Profiles & Environment Management

Maintain `application.properties` with environment-agnostic baselines and specific overrides per profile:

```properties
# application.properties (Common)
spring.application.name=rental-service
spring.jpa.open-in-view=false
spring.jpa.hibernate.ddl-auto=validate
spring.liquibase.change-log=classpath:db/changelog/db.changelog-master.xml
server.error.include-message=never

# application-dev.properties
spring.datasource.url=jdbc:h2:mem:rentaldb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# application-prod.properties
spring.jpa.show-sql=false
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.connection-timeout=20000
```
