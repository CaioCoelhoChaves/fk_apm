package {{PACKAGE_NAME}}.domain;

import com.github.f4b6a3.ulid.UlidCreator;
import org.hibernate.HibernateException;
import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.id.IdentifierGenerator;

import java.io.Serializable;
import java.util.UUID;

/**
 * High-performance, B+Tree friendly sequential identifier generator.
 * Combines 48-bit timestamp with cryptographic randomness, avoiding
 * clustered index page fragmentation caused by standard UUID v4.
 */
public class UlidGenerator implements IdentifierGenerator {

    @Override
    public Serializable generate(SharedSessionContractImplementor session, Object object) 
            throws HibernateException {
        return UlidCreator.getMonotonicUlid().toUuid();
    }

    @Override
    public boolean supportsJdbcBatchInserts() {
        return true;
    }
}
