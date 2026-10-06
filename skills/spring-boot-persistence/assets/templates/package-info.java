@GenericGenerator(
        name = "ulid_generator",
        strategy = "{{PACKAGE_NAME}}.domain.UlidGenerator"
)
package {{PACKAGE_NAME}}.domain;

import org.hibernate.annotations.GenericGenerator;
