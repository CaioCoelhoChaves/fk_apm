# Quickstart: Validação e Testes End-to-End da Modernização do Linear Workflow

**Issue**: [FAL-58](https://linear.app/fallkey/issue/FAL-58/featworkflow-modernizar-linear-workflow-com-ciclo-draft-prs-e) | **Branch**: `feat/FAL-58-modernizar-linear-workflow-draft-prs` | **Date**: 2026-10-29

Este guia fornece cenários de validação executáveis para verificar a conformidade de ponta a ponta da modernização da skill `linear-workflow`.

---

## Pré-requisitos

1. **Python 3.8+** instalado e disponível no PATH (`python --version`).
2. **Git** configurado localmente (`git --version`).
3. **GitHub CLI (`gh`)** autenticado (`gh auth status`).
4. **Variável de Ambiente Linear**: `LINEAR_API_KEY` definida ou presente em arquivo `.env`.

---

## Cenário 1: Suíte de Testes Unitários Automatizados

Valida 100% das funções de parsing, sanitização, subcomandos `sync-boards`, `setup-board`, regras de bloqueio do estado `Done`, e isolamento de worktree.

```bash
# Executar a suíte de testes unitários do linear-workflow
python -m unittest skills/linear-workflow/tests/test_linear_api.py
```

### Resultado Esperado:
- Todos os testes executados com sucesso (`OK`), sem falhas ou erros.
- Cobertura validando:
  - Mapeamento de 6 estados (`Backlog`, `Planned`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`).
  - Bloqueio estrito de transição automatizada para `Done`.
  - Reconciliação e dry-run do subcomando `sync-boards`.
  - Comportamento de worktree efêmero.

---

## Cenário 2: Validação Estática de Artefatos do Spec Kit (`validate-plan`)

Valida a presença das 5 seções arquiteturais obrigatórias em `plan.md` e a integridade de arquivos impactados.

```bash
# Validar os artefatos do card FAL-58
python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-58
```

### Resultado Esperado:
- Saída JSON indicando sucesso:
  ```json
  {
    "success": true,
    "valid": true,
    "sections_found": [
      "Diagnóstico e Contexto",
      "Arquitetura da Solução",
      "Checklist de Arquivos Impactados",
      "Estratégia de Testes",
      "Plano Gitflow"
    ],
    "errors": []
  }
  ```

---

## Cenário 3: Auditoria e Sincronização de Boards em Modo Simulação (`sync-boards --dry-run`)

Inspeciona os quadros do Linear e lista as ações planejadas sem efetuar mutações no Linear.

```bash
# Executar inspeção dry-run no time FallKey
python skills/linear-workflow/scripts/linear_api.py sync-boards --dry-run
```

### Resultado Esperado:
- O script identifica o time `FallKey` e aponta a proposta de migração do estado legado `Technical Analysis` para `Planned` na posição `1.0` com cor `#F2C94C`.
- Nenhuma mutação é enviada à API do Linear em modo `--dry-run`.

---

## Cenário 4: Verificação de Bloqueio da Transição para `Done`

Testa a regra de segurança que proíbe agentes de realizarem transições para o estado `Done`.

```bash
# Tentativa de avançar para Done via CLI
python skills/linear-workflow/scripts/linear_api.py update-issue "FAL-58" --state "Done"
```

### Resultado Esperado:
- A CLI rejeita a operação com erro explícito informando que `Done` é restrito a desenvolvedores humanos após merge do PR.

---

## Cenário 5: Verificação de Validação de Argumento Obrigatório `<CARD-ID>`

Verifica que comandos do Spec Kit abortam quando acionados sem o identificador do card.

```bash
# Simulação de chamada sem card
python .specify/scripts/python/check_prerequisites.py --json
```

### Resultado Esperado:
- O sistema orienta o uso da sintaxe correta parametrizada: `/speckit-plan <CARD-ID>` (ex: `/speckit-plan FAL-58`).
