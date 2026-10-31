# Quickstart: Validação do Fluxo Contínuo e Autônomo do Spec Kit

Este guia fornece cenários práticos e verificáveis para validar a execução autônoma do Spec Kit sem Consent Gates entre fases e com revisão centralizada no GitHub.

---

## Pré-requisitos

1. **Repositório Git**: Com remote configurado (`origin`) e credenciais do GitHub (`gh auth status`).
2. **Linear API Key**: Configurada no ambiente (`LINEAR_API_KEY`) ou `.linear.json`.
3. **Ambiente Python**: Python 3.8+ instalado e funcional.

---

## Cenário 1: Fluxo Sequencial Autônomo (`specify` ➔ `plan` ➔ `tasks`)

### Objetivo
Comprovar que uma funcionalidade pode evoluir de uma ideia para uma especificação e plano técnico completo sem nenhuma interrupção de pergunta interativa no chat.

### Passos de Execução

1. **Especificação**:
   ```bash
   /speckit-specify "Implementar exportação de relatórios em formato CSV"
   ```
   *Resultado esperado*:
   - Branch `feat/FAL-XX-exportacao-csv` criada.
   - Arquivos `spec.md` e `checklists/requirements.md` gerados.
   - Draft PR aberto no GitHub via `gh pr create --draft`.
   - Card no Linear criado em `Backlog` vinculado ao PR.
   - Nenhuma pergunta (`ask_question`) exibida no chat.

2. **Planejamento Técnico**:
   ```bash
   /speckit-plan FAL-XX
   ```
   *Resultado esperado*:
   - Arquivos `plan.md` (com as 5 seções obrigatórias), `research.md`, `data-model.md`, `quickstart.md` gerados.
   - Commits enviados para a branch remota do Draft PR.
   - Card no Linear avançado para `Planned`.
   - Comentário técnico registrado na issue.
   - Conclusão sem perguntas interativas no chat.

3. **Geração de Tarefas**:
   ```bash
   /speckit-tasks FAL-XX
   ```
   *Resultado esperado*:
   - Arquivo `tasks.md` gerado com checklist de tarefas.
   - Validação estática `validate-plan` executada com sucesso.
   - Commits enviados para o Draft PR.
   - Card no Linear avançado para `Todo`.
   - Conclusão sem interrupções.

---

## Cenário 2: Revisão no GitHub e Clarificação Autônoma

### Objetivo
Validar que alterações realizadas pelo desenvolvedor no GitHub são consumidas e sincronizadas pelo `/speckit-clarify`.

### Passos de Execução

1. No GitHub, acesse a branch do Draft PR e edite `specs/<feature>/spec.md` inserindo um detalhe adicional de requisito.
2. No chat da IDE, execute:
   ```bash
   /speckit-clarify FAL-XX
   ```
3. *Resultado esperado*:
   - O comando executa `git pull --rebase origin <branch>`.
   - Lê e valida as alterações introduzidas no GitHub.
   - Harmoniza os checklists e comita as melhorias na branch.
   - Envia o push ao GitHub e reporta a conclusão sem travar o usuário no chat.

---

## Cenário 3: Salvaguarda da Transição Manual para `Done`

### Objetivo
Garantir que a transição para `Done` permaneça estritamente restrita a intervenção humana após o merge do PR.

### Passos de Execução

1. Conclua a implementação via `/speckit-implement FAL-XX`.
2. Verifique que o PR foi promovido a ready e o Linear está em `In Review`.
3. Verifique que o comando finalizou sem tentar mover para `Done`.
4. O desenvolvedor realiza o merge do PR no GitHub (`gh pr merge`).
5. O desenvolvedor manualmente marca o card como `Done` no Linear.
