# Quickstart: Validação do comando /fk-new-manual-issue

**Feature**: `055-manual-linear-cards` | **Linear Issue**: [FAL-59](https://linear.app/fallkey/issue/FAL-59/featskills-add-fk-new-manual-issue-command-for-manual-linear-cards)  
**Date**: 2026-10-31 | **Status**: Complete

---

## 1. Pré-Requisitos

1. Python 3.8+ instalado e acessível via terminal (`python` ou `python3`).
2. Credenciais de API do Linear configuradas via variável de ambiente `LINEAR_API_KEY` ou arquivo `.env` gitignorado.
3. Repositório `fk_apm` configurado.

---

## 2. Cenários de Validação Executáveis

### Cenário 1: Criação de Card Manual Individual via CLI
Valida a criação direta de um único card com parâmetros de linha de comando.

**Comando de Execução**:
```bash
python skills/linear-workflow/scripts/linear_api.py create-manual-issues \
  --title "[Teste] Validação de Conta Operacional" \
  --description "## Contexto da Tarefa Manual\nCriar credenciais no dashboard externo.\n\n## Ações Manuais a Executar\n- [ ] Acessar portal\n- [ ] Gerar API key\n\n## Critérios de Conclusão\n- [ ] Chave gerada com sucesso"
```

**Resultado Esperado**:
- Resposta JSON com `"success": true`.
- Retorno de 1 issue contendo `id`, `identifier` (ex: `FAL-XX`), `state: "Backlog"` e `labels: ["manual"]`.
- A tag `manual` é associada automaticamente (ou criada caso não existisse previamente).

---

### Cenário 2: Criação em Lote via Arquivo JSON (`--batch-file`)
Valida a capacidade de processar múltiplos cards operacionais de uma única vez.

**Passo 1: Criar arquivo de teste temporário (`.tmp-test-batch.json`)**:
```json
{
  "issues": [
    {
      "title": "[Teste Batch 1] Registro de Domínio",
      "description": "## Contexto da Tarefa Manual\nRegistrar domínio institucional.\n\n## Ações Manuais a Executar\n- [ ] Comprar domínio no provedor\n- [ ] Apontar DNS"
    },
    {
      "title": "[Teste Batch 2] Assinatura de Contrato de Gateway",
      "description": "## Contexto da Tarefa Manual\nValidação jurídica de contrato de pagamentos.\n\n## Ações Manuais a Executar\n- [ ] Assinar contrato Docusign"
    }
  ]
}
```

**Passo 2: Executar subcomando**:
```bash
python skills/linear-workflow/scripts/linear_api.py create-manual-issues --batch-file ".tmp-test-batch.json"
```

**Resultado Esperado**:
- Resposta JSON com `"success": true` e `"count": 2`.
- Ambos os cards criados no Linear na coluna `Backlog` com a etiqueta `manual`.

---

### Cenário 3: Validação dos Testes Automatizados Unitários
Garante a integridade do parser CLI, tratamento de erros e chamadas GraphQL simuladas.

**Comando de Execução**:
```bash
python -m unittest skills/linear-workflow/tests/test_linear_api.py
```

**Resultado Esperado**:
- Todos os testes executados com status `OK`.
- Casos de teste específicos para `create-manual-issues` (individual, batch, sanitização, erro de time/projeto) passando sem falhas.

---

### Cenário 4: Verificação de Isolamento Git (Zero Código Alterado)
Confirma que o repositório permanece limpo e nenhuma branch foi criada pelo fluxo de issues manuais.

**Comando de Execução**:
```bash
git status
git branch --list "feat/manual-*"
```

**Resultado Esperado**:
- Nenhuma branch criada para os cards manuais.
- Árvore Git limpa (working tree clean).
