# Quickstart: Validação da Remoção do Rito de Aprovação Final (FAL-74)

**Issue**: [FAL-74](https://linear.app/fallkey/issue/FAL-74/featlinear-workflow-remover-rito-de-aprovacao-final-nas-etapas-speckit) | **Branch**: `feat/FAL-74-remove-consent-gate-rite` | **Date**: 2026-11-23

Este guia documenta os cenários executáveis para validar de ponta a ponta que `/speckit-specify`, `/speckit-plan`, `/speckit-tasks` e `/speckit-implement` operam em fluxo orientado a diálogo sem rito de aprovação final, preservando o Pre-Render no chat, o Consent Gate em `/speckit-taskstoissues` e a paridade em `.agents/`.

---

## Pré-requisitos

1. **Python 3.8+** disponível no PATH (`python --version`).
2. **APM CLI** disponível no PATH (`apm --version`) para sincronização e auditoria de pacotes.
3. Branch ativa `feat/FAL-74-remove-consent-gate-rite`.

---

## Cenário 1: Suíte de Testes Unitários do `linear-workflow`

Executa os testes unitários da CLI e dos contratos textuais das skills/prompts/referências.

```bash
python -m unittest skills/linear-workflow/tests/test_linear_api.py
```

### Resultado Esperado
- Todos os testes passam (`OK`, exit code `0`).
- Verificação automática confirmando:
  - Presença de `Pre-Render`, `Executive Briefing`, `Título Revisado`, `Descrição Atualizada` e flags file-first UTF-8 (`--title`, `--description-file`, `--comment-file`, `--body-file`).
  - Ausência de rito final de aprovação (`"(Recommended) Sim, aprovar"`, `"Editar..."`) em `speckit-specify`, `speckit-plan`, `speckit-tasks` e `speckit-implement` (tanto em `.apm/skills/` quanto em `.apm/prompts/`).
  - Preservação do 3-Stage Consent Gate em `speckit-taskstoissues`.

---

## Cenário 2: Validação Estática dos Artefatos de `FAL-74`

Verifica que os artefatos de especificação, plano e tarefas da feature atendem às 5 seções obrigatórias e ao formato acionável do Spec Kit.

```bash
python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-74
```

### Resultado Esperado
- Durante a fase de planejamento (antes de `/speckit-tasks`): todas as 5 seções e os 20 arquivos mapeados em `plan.md` são validados sem erros estruturais (apenas `tasks.md` pendente até `/speckit-tasks`).
- Após `/speckit-tasks FAL-74`: JSON retorna `"valid": true` e `"errors": []`.

---

## Cenário 3: Auditoria de Ausência de Rito Final vs Exceção em Lote

Inspeciona os contratos dos comandos para confirmar a separação entre execução direta com Pre-Render e Consent Gate em lote.

```bash
git grep -n "Sim, aprovar" -- skills/linear-workflow/
```

### Resultado Esperado
- Nenhuma ocorrência em `speckit-specify`, `speckit-plan`, `speckit-tasks` ou `speckit-implement`.
- Ocorrências preservadas exclusivamente onde o rito de aprovação em lote permanece ativo (`speckit-taskstoissues` e eventuais descrições explícitas dessa exceção na documentação/constituição).

---

## Cenário 4: Sincronização `.agents/` e Validação APM

Recompila/instala as skills locais para garantir zero divergência entre `skills/linear-workflow/` e `.agents/skills/` (`SC-003`).

```bash
apm install
```

### Resultado Esperado
- Arquivos implantados em `.agents/skills/linear-workflow/` e `.agents/skills/speckit-*` possuem exatamente o mesmo conteúdo dos arquivos fonte em `skills/linear-workflow/` e hashes atualizados em `apm.lock.yaml`.
- Veja detalhes normativos completos em [contracts/skill-execution-modes.md](contracts/skill-execution-modes.md) e [data-model.md](data-model.md).
