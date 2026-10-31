# Contract: GitHub Sync & Clarification for `/speckit-clarify`

Este contrato define a mecânica de sincronização entre o repositório remoto (GitHub), o desenvolvedor e o comando `/speckit-clarify <CARD-ID>`.

---

## 1. Origem dos Feedbacks e Modificações

O desenvolvedor pode fornecer feedback ou modificar a especificação de duas formas primárias no GitHub:

1. **Edição Direta de Arquivos na Branch Remota**:
   - Edições em `specs/<feature>/spec.md` ou `checklists/requirements.md` via Web UI do GitHub ou push de terminal local.
2. **Comentários e Sugestões no Pull Request**:
   - Comentários na aba *Conversation* ou *Files Changed* do Draft PR.

---

## 2. Fluxo de Sincronização do `/speckit-clarify`

Quando invocado via `/speckit-clarify <CARD-ID>`:

```text
[Início]
   │
   ▼
[Entrar em .worktrees/<CARD-ID>]
   │
   ▼
[git fetch origin <branch>]
   │
   ▼
[git pull --rebase origin <branch>]
   │
   ├── Conflito de Merge? ──► [Aborta com orientações claras ao desenvolvedor]
   │
   ▼
[Verificar spec.md e pendências técnicas]
   │
   ▼
[Resolver itens marcados como [NEEDS CLARIFICATION] ou sugestões apontadas]
   │
   ▼
[Atualizar spec.md e checklists/requirements.md]
   │
   ▼
[git commit -m "docs(clarify): resolve ambiguities and sync GitHub review for <CARD-ID>"]
   │
   ▼
[git push origin <branch>]
   │
   ▼
[Emitir Executive Report no Chat com link do PR e orientação para /speckit-plan <CARD-ID>]
```

---

## 3. Garantias e Invariantes

- Nenhuma perda de trabalho remoto: o comando sempre puxa antes de comitar.
- Idempotência: caso não haja clarificações adicionais ou o `spec.md` já esteja consistente, o comando informa que a especificação está pronta para planejamento.
- Zero question prompts no chat: o desenvolvedor orienta a IA pelo próprio GitHub ou argumentos do comando.
