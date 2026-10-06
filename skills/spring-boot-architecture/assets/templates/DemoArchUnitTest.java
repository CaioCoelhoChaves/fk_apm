package {{PACKAGE_NAME}};

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
                .importPackages("{{PACKAGE_NAME}}");
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
                .because("A camada de controle deve sempre interagir exclusivamente com a camada de serviço")
                .check(importedClasses);
    }

    @Test
    @DisplayName("Garantir convenção de nomenclatura")
    public void namingConventionsMustBeRespected() {
        classes().that().resideInAPackage("..controller..")
                .should().haveSimpleNameEndingWith("Controller")
                .check(importedClasses);

        classes().that().resideInAPackage("..service..")
                .should().haveSimpleNameEndingWith("Service")
                .check(importedClasses);
    }
}
