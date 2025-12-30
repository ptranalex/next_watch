# VSCode User Settings Cleanup Guide

## Overview

To complete the VSCode settings reorganization, you need to remove Python-specific settings from your **User Settings** (global settings). These settings should be managed at the workspace or folder level, not globally.

## User Settings Location

**File:** `/Users/alex/Library/Application Support/Cursor/User/settings.json`

Or access via: `Cmd+Shift+P` → "Preferences: Open User Settings (JSON)"

## Settings to Remove

Remove these lines from your User settings:

### 1. Python Interpreter Path

```json
"python.defaultInterpreterPath": "",
```

**Why remove:** Each project should define its own interpreter. Having this in User settings can cause conflicts.

### 2. Python Formatting Provider

```json
"python.formatting.provider": "black",
```

**Why remove:** We're now using Ruff for formatting (defined in workspace), not Black.

### 3. Python Language-Specific Settings

```json
"[python]": {
  "editor.defaultFormatter": "ms-python.black-formatter",
  "editor.formatOnSave": true
},
```

**Why remove:**

- Workspace now defines Ruff as the formatter
- Format-on-save is disabled (pre-commit hooks handle formatting)

### 4. JavaScript Formatting (Optional - if it conflicts)

```json
"[javascript]": {
  "editor.formatOnSave": true
},
```

**Why remove:** Workspace now manages format-on-save settings for consistency.

## What to Keep

Keep these in your User settings (personal preferences):

```json
{
  "terminal.integrated.fontFamily": "MesloLGS NF",
  "terminal.integrated.cursorStyle": "line",
  "terminal.integrated.lineHeight": 1.5,
  "workbench.colorTheme": "Default Dark Modern",
  "editor.fontSize": 13,
  "terminal.integrated.fontSize": 11,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.mypy_cache": true,
    "**/.pytest_cache": true,
    "**/.venv": true,
    "**/.DS_Store": true,
    "**/dist": true,
    "**/build": true,
    "**/htmlcov": true
  },
  "search.exclude": {
    "**/__pycache__": true,
    "**/dist": true,
    "**/build": true,
    "**/.venv": true
  }
  // ... other personal preferences
}
```

## After Cleanup

Once you've removed the Python-specific settings:

1. **Reload VSCode/Cursor**: `Cmd+Shift+P` → "Developer: Reload Window"
2. **Open the workspace**: `File` → `Open Workspace from File...` → select `next_watch.code-workspace`
3. **Verify settings**: Check that Python formatting now uses Ruff (not Black)
4. **Test**: Make a small change to a Python file and commit it - pre-commit hooks should handle formatting

## Settings Hierarchy Reference

After cleanup, your settings will follow this hierarchy:

```
┌─────────────────────────────────────────────┐
│  User Settings                              │
│  (Personal preferences only)                │
│  - Theme, fonts, general editor behavior    │
└─────────────────────┬───────────────────────┘
                      │ (inherits)
                      ▼
┌─────────────────────────────────────────────┐
│  Workspace Settings                         │
│  (next_watch.code-workspace)                │
│  - Python: Ruff formatter, no format-on-save│
│  - TypeScript: Prettier, no format-on-save  │
│  - Testing: pytest enabled                  │
└─────────────────────┬───────────────────────┘
                      │ (inherits + overrides)
                      ▼
┌─────────────────────────────────────────────┐
│  Folder Settings                            │
│  (each app/lib .vscode/settings.json)       │
│  - Python interpreter path (.venv/bin/py)   │
│  - Analysis paths (../../libs/kafka/src)    │
└─────────────────────────────────────────────┘
```

## Troubleshooting

### Format-on-save still happening?

- Check User settings - make sure `"editor.formatOnSave"` is not set to `true` globally
- Reload window after making changes

### Black still being used instead of Ruff?

- Verify Black extension settings are removed from User settings
- Ensure Ruff extension is installed
- Check workspace is open (not just a folder)

### Import resolution not working?

- Verify you're using the multi-root workspace (`next_watch.code-workspace`)
- Check folder settings have correct `python.analysis.extraPaths`
- Reload window

## Questions?

If you run into issues after cleanup, see:

- [VSCode Setup section in README](../README.md#vscode-setup)
- [Pre-commit Setup](./PRECOMMIT_SETUP.md)
