---
name: fk-new-issue
description: Planejamento, decomposição e criação atômica de novos cards no Linear com o protocolo de Consent Gate em 3 etapas. Use quando o usuário invocar /fk-new-issue ou solicitar criação/planejamento de tarefas no Linear.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-new-issue: Planejamento & Criação Atômica de Tarefas no Linear

Este comando orquestra o rito de planejamento e decomposição de tarefas no Linear, aplicando integralmente o protocolo de **Consent Gate em 3 etapas** e as diretrizes da skill `linear-workflow`.

---

## Protocolo Inviolável em 3 Etapas

### 1. Etapa 1: Leitura, Decomposição & Apresentação (Zero Mutação)
- **Localização do Projeto**: Localize o projeto pai no Linear usando o MCP `linear_list_projects` ou o helper CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py find-project "<nome-do-projeto>"
  ```
- **Classificação de Componente / Repositório**: Identifique a natureza e a stack do repositório para definir o tagueamento adequado:
  - **`Front`**: Aplicações e pacotes de interface gráfica (Flutter, React, Vue, Angular, Next.js, Web, Mobile).
  - **`Back`**: Serviços, APIs e servidores de backend (Spring Boot, Node.js API, Java, Python FastAPI/Django/Flask, Go, Rust).
  - **`Feature` ou Sem Tag (Omissão de `--label`)**: Repositórios de tooling, pacotes de skills/prompts de IA (como `fk_apm`), CLIs, automações, bibliotecas agnósticas ou infraestrutura. Nesses repositórios, **não force `Back`** pela mera presença de scripts auxiliares em Python ou Shell; aplique `--label "Feature"` (para novas funcionalidades/melhorias) ou omita o argumento `--label`.
- **Decomposição em Chat**: Apresente no chat a proposta completa de tarefas estruturadas:
  - Título objetivo no padrão `<tipo>(<escopo>): <descrição>`.
  - Descrição técnica com critérios de aceitação.
  - Label aplicável (`Front`, `Back`, `Feature` ou sem tag, conforme a natureza do repositório).
  - Status inicial proposto: **`Backlog` por padrão** (a demanda ainda passará por `/fk-technical-analysis`). Proponha `Todo` apenas como exceção explícita (card trivial ou com escopo técnico e planejamento 100% resolvidos desde a concepção), justificando a exceção na tabela de decomposição e no Consent Gate.
- ⚠️ **Zero Mutação**: **NÃO crie nenhum card no Linear nesta etapa.**

> [!IMPORTANT]
> **Proibição de Consent Gate Cego (Renderização Prévia Obrigatória)**:
> É **estritamente proibido** invocar `ask_question` / `AskUserQuestion` sem antes emitir integralmente no texto visível do chat a tabela ou lista detalhada com todos os cards propostos (título, descrição estruturada, critérios de aceitação, label e status inicial). O desenvolvedor jamais deve receber a caixa de pergunta sem visualizar a proposta completa renderizada acima.

### 2. Etapa 2: Consent Gate Interativo (Confirmação Explícita)
- Certifique-se de que toda a proposta da Etapa 1 já foi emitida no corpo textual da resposta e apresente a pergunta de consentimento invocando a **ferramenta nativa de perguntas** do harness, incluindo obrigatoriamente um **resumo conciso do plano** no próprio texto de `question` como salvaguarda:
  - **Google Antigravity**: chame `ask_question`:
    ```json
    {
      "questions": [
        {
          "question": "Resumo do plano (N cards em Backlog): 1) <título-1> [<label-ou-sem-tag>]; 2) <título-2> [<label-ou-sem-tag>]. O escopo e a divisão dos cards estão alinhados? Posso criá-los no Linear sob o status Backlog (padrão)?",
          "options": [
            "(Recommended) Sim, aprovar",
            "Editar..."
          ],
          "is_multi_select": false
        }
      ]
    }
    ```
  - **Claude Code**: chame `AskUserQuestion` com o resumo conciso na pergunta e opções `["Sim, aprovar", "Editar..."]`.
  - **OpenCode v2**: chame a ferramenta nativa de pergunta com o resumo conciso na pergunta e opções `["Sim, aprovar", "Editar..."]`.
  - **Fallback Textual (Cursor, Copilot, Gemini CLI ou sem tool nativa)**: apresente em bloco Markdown destacado com o resumo conciso e opções numeradas (`1. (Recomendado) Sim, aprovar` e `2. Editar...`).
- **Tratamento das Opções**:
  - `(Recommended) Sim, aprovar`: avança imediatamente para a **Etapa 3 (Execução Atômica)**.
  - `Editar...`: permite ao desenvolvedor indicar correções ou novos cards em texto livre. O agente **retorna à Etapa 1**, refina a divisão de tarefas no chat e apresenta novo Consent Gate. **Zero mutação é estritamente mantida**.

### 3. Etapa 3: Execução Atômica
- Após aprovação, crie cada card no Linear via MCP (`linear_create_issue`) ou CLI (omita `--label` caso o card não possua tag em repositórios de tooling/skills):
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py create-issue \
    --team-id "<team-id>" \
    --project-id "<project-id>" \
    --title "<título>" \
    --description "<descrição>" \
    --state "Backlog"   # use "Todo" somente na exceção explícita aprovada no Consent Gate \
    --label "<Front, Back ou Feature>"  # omita --label se optado por sem tag em projetos de tooling/skills
  ```
- Informe o desenvolvedor com links diretos e identificadores criados (ex: `FAL-10`).
