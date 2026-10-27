---
description: Planejamento, decomposição e criação atômica de novos cards no Linear com consent gate em 3 etapas
argument-hint: "[contexto ou requisitos]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# /fk-new-issue: Planejamento & Criação Atômica de Tarefas no Linear

Execute o rito de planejamento e decomposição de tarefas seguindo rigorosamente a skill `linear-workflow` e o protocolo de **Consent Gate em 3 etapas**:

Contexto fornecido: $ARGUMENTS

## Diretrizes de Execução
1. **Etapa 1 - Leitura & Apresentação (Zero Mutação)**:
   - Localize o projeto pai no Linear usando `find-project` ou MCP `linear_list_projects`.
   - Analise os requisitos e decomponha-os em tarefas atômicas no chat (título, descrição estruturada, critérios de aceitação, status inicial `Backlog` por padrão e label: `Front`, `Back`, ou `Feature`/sem tag para repositórios de tooling, skills e infraestrutura — nunca force `Back` apenas por scripts auxiliares em Python/Shell).
   - **Renderização Prévia Obrigatória**: Emita integralmente no texto visível do chat a tabela/lista detalhada com todos os cards propostos antes de acionar a pergunta da Etapa 2. **Não crie nenhum card no Linear nesta etapa.**
2. **Etapa 2 - Consent Gate Interativo (Confirmação Explícita)**:
   - **Proibido Consent Gate Cego**: Só invoque `ask_question` / `AskUserQuestion` após renderizar toda a proposta no texto do chat, e inclua um resumo conciso dos cards (`Resumo do plano (N cards em Backlog): 1) <título> [<label>]...`) dentro do próprio campo `question` da ferramenta interativa ou fallback textual com opções `(Recommended) Sim, aprovar` e `Editar...`.
   - Se `Editar...`: receba ajustes de escopo em texto livre, retorne à Etapa 1 para atualizar a decomposição e reapresente o Consent Gate. Zero mutação no Linear até aprovação explícita.
   - Aguarde `Sim, aprovar` antes de qualquer chamada de mutação.
3. **Etapa 3 - Execução Atômica**:
   - Após aprovação, crie os cards no Linear via CLI (`create-issue --description-file "<path>"`) ou MCP (`linear_create_issue`), gravando a descrição em arquivo UTF-8 temporário para evitar corrupção de crases (`` ` ``) e aspas duplas no shell.
   - Apresente o sumário final com links diretos e identificadores (ex: `FAL-10`).
