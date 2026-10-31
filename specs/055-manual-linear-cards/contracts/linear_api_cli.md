# CLI Contract: `linear_api.py create-manual-issues`

**Scope**: Interface CLI para criação individual ou em lote de cards manuais no Linear.  
**File**: `skills/linear-workflow/scripts/linear_api.py`

---

## 1. Subcomando: `create-manual-issues`

### 1.1 Invocação em Lote (Recomendado)
```bash
python skills/linear-workflow/scripts/linear_api.py create-manual-issues \
  [--team-id <UUID>] \
  [--project-id <UUID>] \
  --batch-file <path/to/batch.json>
```

#### Schema do Arquivo JSON de Lote (`batch.json`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ManualIssuesBatch",
  "type": "object",
  "properties": {
    "team_id": { "type": "string" },
    "project_id": { "type": "string" },
    "issues": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["title"],
        "properties": {
          "title": { "type": "string", "minLength": 1, "maxLength": 255 },
          "description": { "type": "string" },
          "description_file": { "type": "string" },
          "priority": { "type": "integer", "minimum": 0, "maximum": 4 }
        }
      }
    }
  },
  "required": ["issues"]
}
```

### 1.2 Invocação Individual via Linha de Comando
```bash
python skills/linear-workflow/scripts/linear_api.py create-manual-issues \
  [--team-id <UUID>] \
  [--project-id <UUID>] \
  --title "Título da Tarefa Manual" \
  --description-file <path/to/desc.md> \
  [--priority <0-4>]
```

---

## 2. Saída JSON (Stdout)

### 2.1 Sucesso
Código de saída: `0`.
```json
{
  "success": true,
  "count": 2,
  "issues": [
    {
      "id": "e4a2c161-b489-4e7a-9db1-112233445566",
      "identifier": "FAL-60",
      "title": "Configurar credenciais de produção no Gateway",
      "url": "https://linear.app/fallkey/issue/FAL-60/configurar-credenciais...",
      "state": "Backlog",
      "labels": ["manual"]
    },
    {
      "id": "f5b3d272-c590-4f8b-0ec2-223344556677",
      "identifier": "FAL-61",
      "title": "Emitir certificado TLS para domínio institucional",
      "url": "https://linear.app/fallkey/issue/FAL-61/emitir-certificado-tls...",
      "state": "Backlog",
      "labels": ["manual"]
    }
  ]
}
```

### 2.2 Falha
Código de saída: `1` (ou JSON com `"success": false`).
```json
{
  "success": false,
  "error": "Team ID could not be resolved from environment or Linear projects",
  "issues": []
}
```
