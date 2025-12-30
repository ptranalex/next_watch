# IDE Configuration Complete ✅

Your VSCode/Cursor IDE is now configured to catch linting and type errors in real-time!

## What Was Configured

### 1. Workspace-Level Settings (`next_watch.code-workspace`)

- ✅ **Ruff linting** enabled with `onType` checking
- ✅ **Auto-format on save** enabled for Python files
- ✅ **Auto-fix Ruff errors** on save
- ✅ **Auto-organize imports** on save
- ✅ **MyPy type checker** configured
- ✅ **Pylance strict mode** enabled for comprehensive type checking
- ✅ **Workspace-wide diagnostics** to see errors across all apps

### 2. Per-App Settings Created

Created `.vscode/settings.json` for each Python app:

- ✅ `apps/backend-api/` - with movie-storage, cache, config, fast-core, kafka libs
- ✅ `apps/auth-api/` - already existed, kept as-is
- ✅ `apps/bff-api/` - with cache, config, fast-core, kafka libs
- ✅ `apps/recommendation-api/` - with cache, config, fast-core, kafka libs
- ✅ `apps/search-api/` - with cache, config, fast-core libs
- ✅ `apps/ml-api/` - with cache, config, fast-core libs
- ✅ `apps/data-importer/` - with movie-storage, config libs

Each app configuration includes:

- Python interpreter path (`.venv/bin/python`)
- Extra paths for internal library imports
- Auto-complete paths
- PYTHONPATH and MYPYPATH environment variables

## Required VSCode Extensions

Make sure you have these extensions installed:

1. **Python** (`ms-python.python`) - Core Python support
2. **Pylance** (`ms-python.vscode-pylance`) - Fast type checking
3. **Mypy Type Checker** (`ms-python.mypy-type-checker`) - Strict type checking
4. **Ruff** (`charliermarsh.ruff`) - Fast Python linting & formatting
5. **Prettier** (`esbenp.prettier-vscode`) - For TypeScript/JavaScript formatting

## How to Activate

1. **Close any open VSCode/Cursor windows**
2. **Open the workspace file:**

   ```bash
   cd /Users/alex/Sandbox/next_watch
   code next_watch.code-workspace
   ```

   (Or if using Cursor: `cursor next_watch.code-workspace`)

3. **Reload the window:**

   - Press `Cmd+Shift+P`
   - Type "Developer: Reload Window"
   - Press Enter

4. **Install extensions** (if prompted):
   - VSCode will show recommended extensions
   - Click "Install All" or install individually

## Verification Steps

### Test 1: Real-Time Linting

1. Open `apps/auth-api/src/auth_api/cli/commands/users.py`
2. You should see yellow/red squiggles on lines with errors
3. Hover over squiggles to see error messages

### Test 2: Problems Panel

1. Press `Cmd+Shift+M` to open Problems panel
2. You should see all linting and type errors listed
3. Click on any error to jump to that line

### Test 3: Auto-Format on Save

1. Open any Python file
2. Add some trailing whitespace at the end of a line
3. Save the file (`Cmd+S`)
4. Whitespace should be automatically removed

### Test 4: Import Organization

1. Add a random import at the bottom of the imports section
2. Save the file
3. Imports should be automatically sorted

## Error Coverage

Your IDE will now catch these errors **before commit**:

### Ruff Errors

- ✅ B904: Missing exception chaining (`raise ... from err`)
- ✅ W291: Trailing whitespace (auto-fixed)
- ✅ W293: Blank line whitespace (auto-fixed)
- ✅ F841: Unused variables
- ✅ E722: Bare `except` clauses
- ✅ E402: Module import order (auto-fixed)
- ✅ SIM105: Simplify code patterns
- ✅ All other Ruff rules from `pyproject.toml`

### Type Errors (Pylance + MyPy)

- ✅ Missing imports
- ✅ Type mismatches
- ✅ Untyped function calls
- ✅ Any types from unimported modules
- ✅ Undefined variables
- ✅ All MyPy strict mode checks

## Troubleshooting

### "Import could not be resolved" errors for internal libs

- Make sure the `.venv` for that app exists
- Run `hatch shell` in the app directory
- Run `hatch run install-libs` to install internal dependencies

### Linting is slow

- Change `"python.analysis.diagnosticMode": "workspace"` to `"openFilesOnly"` in workspace settings
- This will only check currently open files instead of all files

### MyPy not showing errors

- Make sure MyPy extension is installed
- Check that `.venv/bin/python` exists for each app
- Verify `pyproject.toml` has `[tool.mypy]` configuration

### Ruff not formatting on save

- Check that Ruff extension is installed and enabled
- Verify `"editor.formatOnSave": true` in workspace settings
- Make sure the file is saved as Python (check bottom-right of VSCode)

## Performance Notes

- **First load**: Pylance will index all files (takes 30-60 seconds)
- **Workspace diagnostics**: Checks all apps simultaneously (may be slower on large repos)
- **MyPy**: Runs per-workspace folder, respects `pyproject.toml` configs
- **Ruff**: Very fast, runs on every keystroke

## Next Steps

Now that your IDE is configured, you can:

1. Fix the remaining linting errors in `auth-api` (33 Ruff errors)
2. Address MyPy type errors (130 errors from missing imports)
3. Run pre-commit to ensure everything passes:
   ```bash
   git add .
   git commit -m "your message"
   ```

The pre-commit hooks should pass cleanly once the IDE shows no errors!

## Summary

✅ **Workspace configured** with Ruff + Pylance + MyPy
✅ **6 apps configured** with proper interpreter and lib paths
✅ **Real-time error detection** enabled
✅ **Auto-formatting** on save
✅ **No more commit surprises!**

Happy coding! 🚀
