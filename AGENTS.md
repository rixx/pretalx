# AGENTS.md

This file provides guidance for AI agents working with this repository.

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**
```bash
bd ready --json
```

**Create new issues:**
```bash
bd create "Issue title" -t bug|feature|task -p 0-4 --json
bd create "Issue title" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**
```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**
```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### MCP Server (Recommended)

If using Claude or MCP-compatible clients, install the beads MCP server:

```bash
pip install beads-mcp
```

Add to MCP config (e.g., `~/.config/claude/config.json`):
```json
{
  "beads": {
    "command": "beads-mcp",
    "args": []
  }
}
```

Then use `mcp__beads__*` functions instead of CLI commands.

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and QUICKSTART.md.

## Form Configuration Architecture

This section documents the `form_config` feature for custom service instance forms.

### Overview

The portal generates forms for creating/editing Kubernetes service instances. Two form types exist:

1. **Expert Form** (auto-generated): All fields from CRD OpenAPI schema
2. **Custom Form** (form_config): User-friendly subset configured by admins

### Key Components

#### Models & Schema
- **ServiceDefinition.form_config**: JSONField storing custom form configuration
- **Schema**: `src/servala/core/schemas/form_config_schema.json` (JSON Schema draft-07)
- **Validation**: `src/servala/core/forms.py` ServiceDefinitionAdminForm.clean() (lines 164-179)

#### Form Generation Flow
```
1. ControlPlaneCRD.custom_model_form_class (service.py:516-529)
   └─> Checks if form_config exists and has fieldsets
   └─> Calls generate_custom_form_class() if configured

2. generate_custom_form_class() (crd/forms.py:356-389)
   └─> Creates form class dynamically using ModelFormMetaclass
   └─> Includes fields from form_config.fieldsets[].fields[]
   └─> Base class: CustomFormMixin + ModelForm

3. CustomFormMixin.__init__() (crd/forms.py:266-277)
   └─> Calls _apply_field_config()

4. CustomFormMixin._apply_field_config() (crd/forms.py:279-314)
   └─> Applies form_config settings to each field:
       - label, help_text, required
       - widget type (textarea, array widget)
       - validators (min/max for numbers)
```

#### View Integration
- **Create**: ServiceOfferingDetailView (frontend/views/service.py:80-234)
  - `get_instance_form()`: Returns expert form (or None)
  - `get_custom_instance_form()`: Returns custom form (or None)
  - Context variables: `service_form` (expert), `custom_service_form` (custom)

- **Update**: ServiceInstanceUpdateView (frontend/views/service.py:409-510)
  - `get_form()`: Returns expert form
  - `get_custom_form()`: Returns custom form (or None)
  - Context variables: `form` (expert), `custom_form` (custom)
  - For custom forms: deep merges form data with existing spec (line 487-488)

#### Template Rendering
- **Template**: `src/servala/frontend/templates/includes/tabbed_fieldset_form.html`
- **Parameters**: `form` (custom form), `expert_form` (expert form)
- **Logic**:
  - If `form` exists: Shows custom form + "Show Expert Mode" toggle button
  - If `form` is None: Shows expert form directly (no toggle)
  - Expert form is in `#expert-form-container` (hidden by default if custom exists)
  - Custom form is in `#custom-form-container`
  - JavaScript: `static/js/expert-mode.js` handles toggle between forms

#### Tab System (Multiple Fieldsets)
- Custom form tabs: `#myTab`, `#myTabContent`, tab IDs are `{{ fieldset.title|slugify }}`
- Expert form tabs: `#expertTab`, `#expertTabContent`, tab IDs are `expert-{{ fieldset.title|slugify }}`
- Uses Bootstrap 5: `data-bs-toggle="tab"`, `data-bs-target="#..."`
- **Important**: Fieldset titles MUST be unique within each form to avoid duplicate IDs

### Form Config Schema Structure

```json
{
  "fieldsets": [
    {
      "title": "Section Name",
      "fields": [
        {
          "type": "text|email|textarea|number|choice|checkbox|array",
          "label": "Field Label",
          "controlplane_field_mapping": "spec.parameters.field.path",
          "help_text": "Optional help text",
          "required": false,

          // Type-specific options:
          "max_length": 100,           // text, textarea
          "rows": 4,                   // textarea
          "min_value": 0,              // number
          "max_value": 100,            // number
          "choices": [["val", "Label"]], // choice
          "min_values": 1,             // array
          "max_values": 10             // array
        }
      ]
    }
  ]
}
```

### Common Patterns

#### Adding New Field Config Options
1. Update schema: `src/servala/core/schemas/form_config_schema.json`
2. Apply in: `CustomFormMixin._apply_field_config()` (crd/forms.py:279-314)
3. Test: Create unit test verifying the option works
4. Document: Update this section

#### Field Mapping
- **controlplane_field_mapping**: Dot-notation path in CRD spec
  - Example: `"spec.parameters.service.fqdn"` maps to `spec: { parameters: { service: { fqdn: "..." }}}`
  - Must map to actual field in CRD OpenAPI schema
  - Special case: `"name"` maps to instance name (required in every form)

#### Form Validation
- Schema validation: Happens on save in Django admin (jsonschema.validate)
- Field validation: Happens when user submits form (Django form.clean())
- Control plane validation: Final validation by Kubernetes API (returns errors from CRD validation)

### Troubleshooting

**No form appears when creating instance**:
- Check: Does ServiceDefinition have form_config? If no, expert form should show
- Check: Does ControlPlaneCRD.model_form_class exist? (needs valid CRD schema)
- Check: Browser console for JS errors

**Form config won't save in admin**:
- Check: JSON Schema validation errors in form
- Check: Field mappings valid for the CRD (ServiceDefinitionAdminForm._validate_field_mappings)

**Custom form fields not applying config**:
- Check: _apply_field_config() is called (verify in debugger)
- Check: Field exists in self.fields dict
- Check: field_config has correct structure (type, controlplane_field_mapping, etc.)

