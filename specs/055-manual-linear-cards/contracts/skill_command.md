# Contract: Prompt e Comando `/fk-new-manual-issue`

**Scope**: Especificação de comportamento e protocolo do comando `/fk-new-manual-issue` nos harnesses de IA.  
**Files**:
- `skills/linear-workflow/.apm/prompts/fk-new-manual-issue.prompt.md`
- `skills/linear-workflow/.apm/skills/fk-new-manual-issue/SKILL.md`
- `.agents/skills/fk-new-manual-issue/SKILL.md`

---

## 1. Assinatura do Comando

```text
/fk-new-manual-issue [<descrição ou lista de tarefas>]
```

### Argumentos:
- Se fornecido, o texto descreve 1 tarefa ou uma lista de múltiplas tarefas operacionais.
- Se omitido, o agente faz uma pergunta rápida ao usuário solicitando o título e os detalhes das ações manuais.

---

## 2. Protocolo de Execução (3-Stage Consent Gate)

### Estágio 1: Pre-Render Gate (Zero Mutação Remota)
O agente processa as instruções e renderiza na conversa do chat uma tabela com todos os cards previstos:

```markdown
### 📋 Proposta de Cards Manuais no Linear

| # | Título | Estado Inicial | Etiqueta | Escopo da Ação Manual |
|---|--------|----------------|----------|------------------------|
| 1 | Configurar credenciais no Gateway de Pagamento | Backlog | manual | Acessar dashboard de pagamentos e gerar chaves de API |
| 2 | Solicitar aprovação de domínio na Apple Developer | Backlog | manual | Submeter documentação no portal Apple Developer |
```

### Estágio 2: Confirmação Interativa
O agente aciona a ferramenta de perguntas interativas (`ask_question` / `AskUserQuestion`):
- Pergunta: "Deseja aprovar a criação de X card(s) manual(is) no Linear na coluna Backlog com a tag 'manual'?"
- Opções:
  - `(Recommended) Sim, aprovar criação no Linear`
  - `Editar lista antes de criar...`

### Estágio 3: Criação Atômica
Caso aprovado:
1. O agente grava as issues em arquivo JSON temporário `.tmp-manual-issues.json` (codificado em UTF-8).
2. O agente executa:
   ```bash
   python skills/linear-workflow/scripts/linear_api.py create-manual-issues --batch-file ".tmp-manual-issues.json"
   ```
3. O agente remove o arquivo temporário `.tmp-manual-issues.json`.
4. O agente exibe o resultado com links diretos para os cards criados no Linear.

---

## 3. Garantia de Isolamento de Código

O comando `/fk-new-manual-issue`:
- NÃO cria branches Git.
- NÃO cria worktrees Git.
- NÃO altera arquivos no repositório.
- NÃO abre Pull Requests.
- Finaliza imediatamente após a confirmação e criação remota no Linear.
