# Research: Fluxo Contínuo e Autônomo do Spec Kit com Revisão no GitHub

Este documento consolida as decisões técnicas, justificativas arquiteturais e alternativas consideradas para eliminar os Consent Gates interativos entre fases do Spec Kit e habilitar um fluxo contínuo de ponta a ponta com revisão centralizada no GitHub (Living Specs Draft PRs).

---

## Decisão 1: Eliminação de Consent Gates Interativos Entre Fases

### Contexto
Atualmente, as fases de especificação e planejamento impõem um "3-Stage Consent Gate" (Pre-Render Gate -> `ask_question` -> mutação Linear). Em ambientes ágeis de desenvolvimento assistido por IA, o desenvolvedor não deseja responder enquetes no chat da IDE a cada transição (`Backlog` ➔ `Planned` ➔ `Todo`), uma vez que a revisão efetiva do trabalho é realizada diretamente no GitHub através do Draft Pull Request criado na fase de especificação.

### Decisão
Eliminar o uso de ferramentas de questionamento síncrono (`ask_question` / `AskUserQuestion`) entre os comandos de ciclo de vida:
- `/speckit-specify`: executa especificação, cria branch, versiona artefatos, abre Draft PR, cria issue no Linear em `Backlog` e reporta conclusão no chat com links.
- `/speckit-plan`: gera `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, comita na branch remota, transiciona issue no Linear para `Planned`, registra comentário executivo e reporta conclusão sem parar para confirmação.
- `/speckit-tasks`: gera `tasks.md`, executa validação estática de integridade, comita na branch remota, transiciona issue no Linear para `Todo` e conclui.
- `/speckit-taskstoissues`: converte tarefas em issues no Linear de forma contínua e determinística.

### Rationale
- Reduz a zero a fricção e o tempo de espera do desenvolvedor durante a geração de especificações e planos.
- Alinha a esteira de planejamento à mesma filosofia já adotada com sucesso em `/speckit-implement` e `/speckit-converge` (execução autônoma com governança centralizada no repositório de código).

### Alternativas Consideradas
1. **Manter consent gate opcional via flag (ex: `--no-interactive`)**:
   - Rejeitado porque introduz complexidade em todos os harnesses e prompts; a intenção do usuário é que a revisão padrão seja feita no GitHub, e não no chat.
2. **Substituir `ask_question` por confirmação textual em streaming**:
   - Rejeitado porque ainda exigiria turnos adicionais de conversação e bloqueio de execução.

---

## Decisão 2: Revisão Centralizada no GitHub (Living Specs Draft PR)

### Contexto
Com a abertura imediata do Pull Request em modo Draft logo na fase de especificação (`/speckit-specify`), todos os artefatos subsequentes (`plan.md`, `tasks.md`, código, testes) são comitados na mesma branch do PR. O GitHub oferece a infraestrutura ideal de revisão: renderização rica de Markdown, diffs linha a linha, sugestões inline e threads de discussão.

### Decisão
Consolidar o Draft PR no GitHub como a única interface de revisão humana durante as etapas de especificação e planejamento:
- O agente no chat limita-se a emitir um **Executive Report** conciso e estruturado, contendo o resumo das ações tomadas, o estado do Linear e links diretos para o PR no GitHub e os artefatos locais.
- Nenhuma mutação de fase aguarda validação no chat; o desenvolvedor inspeciona os artefatos no GitHub no seu próprio tempo.

### Rationale
- Elimina a duplicação entre visualizações incompletas no chat da IDE e o código real no repositório.
- Aproveita recursos nativos do GitHub (code review, sugestões de commit com 1 clique, checks de CI) para validar a documentação técnica.

### Alternativas Consideradas
1. **Emitir diffs completos no chat da IDE**:
   - Rejeitado para evitar estouro de contexto e poluição visual da sessão de chat.

---

## Decisão 3: Sincronização Autônoma do `/speckit-clarify` Integrada ao GitHub

### Contexto
Quando o desenvolvedor revisa a especificação no GitHub, ele pode realizar ajustes diretos (commits na branch do Draft PR) ou deixar comentários/feedbacks nas threads do PR. O `/speckit-clarify` precisa absorver essas mudanças para refinar a especificação sem travar em perguntas no chat.

### Decisão
Atualizar o fluxo do `/speckit-clarify <CARD-ID>` para:
1. Executar `git pull --rebase origin <branch>` no worktree/workspace para integrar quaisquer alterações remotas efetuadas pelo desenvolvedor no GitHub.
2. Ler a versão atualizada de `specs/<feature>/spec.md` e os arquivos de contexto.
3. Se houver marcadores de clarificação (`[NEEDS CLARIFICATION]`) ou orientações específicas passadas como argumento, dirimi-los autonomamente, atualizar o checklist de requisitos (`requirements.md`) e registrar as resoluções no próprio `spec.md`.
4. Comitar as melhorias (`docs(clarify): resolve ambiguities and sync GitHub review for <CARD-ID>`), enviar à branch remota (`git push`) e finalizar reportando a prontidão para `/speckit-plan <CARD-ID>`.

### Rationale
- Fecha o ciclo de feedback assíncrono: o desenvolvedor edita/revisa no GitHub e um simples comando `/speckit-clarify <CARD-ID>` processa o refinamento de forma autônoma.

### Alternativas Consideradas
1. **Exigir cópia e cola dos comentários do PR para o chat**:
   - Rejeitado por ser ineficiente e propenso a erros de formatação.

---

## Decisão 4: Salvaguarda Inegociável da Transição para `Done`

### Contexto
A automação de ponta a ponta não pode comprometer a governança de fechamento de tarefas. A transição de uma issue para `Done` é a declaração formal de entrega em produção/homologação.

### Decisão
Manter e reforçar expressamente em todos os scripts, prompts e na Constituição que:
- **A transição para `Done` é EXCLUSIVA e ESTRITAMENTE manual pelo desenvolvedor após o merge do PR na branch principal (`main` ou `develop`)**.
- Nenhum agente ou comando automatizado possui permissão para mover cards para `Done`.

### Rationale
- Previne fechamento acidental de issues antes do merge e deploy.
- Mantém o desenvolvedor humano como o único árbitro final da aceitação e entrega da funcionalidade.

---

## Decisão 5: Atualização Constitucional (v1.2.0) e Harmonização de Manifestos

### Contexto
O ecossistema `fk_apm` distribui skills e prompts para múltiplos harnesses (Antigravity, Claude Code, Cursor, Copilot, OpenCode). Todas as definições em `skills/linear-workflow/.apm/` e manifestos de skills devem refletir as mesmas regras canônicas.

### Decisão
- Elevar a versão da Constituição para `1.2.0`.
- Atualizar a Seção II e a Seção de Governança da Constituição para formalizar a esteira contínua sem Consent Gates.
- Harmonizar os prompts (`speckit-specify.prompt.md`, `speckit-plan.prompt.md`, `speckit-tasks.prompt.md`, `speckit-clarify.prompt.md`, `speckit-taskstoissues.prompt.md`) e os arquivos `SKILL.md` em `skills/linear-workflow`.
- Atualizar testes de unidade em `test_linear_api.py` para garantir conformidade estática e funcional.
