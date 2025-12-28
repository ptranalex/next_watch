***REMOVED*** Pre-commit Hooks Guide

***REMOVED******REMOVED*** Overview

Each app in the monorepo has isolated pre-commit hooks with custom rules. This ensures code quality while maintaining flexibility for each service.

***REMOVED******REMOVED*** How It Works

1. **File-based triggering**: Hooks only run when files in their app are changed
2. **Per-app rules**: Each app configures its own linting strictness
3. **Fast execution**: Only relevant hooks run, not all hooks

***REMOVED******REMOVED*** Installation

Pre-commit should already be installed via Homebrew. If not:

```bash
brew install pre-commit
```

Then install the git hooks in your repository:

```bash
cd /path/to/next_watch
pre-commit install
```

***REMOVED******REMOVED*** Examples

***REMOVED******REMOVED******REMOVED*** Example 1: Edit Backend API

```bash
***REMOVED*** Edit a file
vim apps/backend-api/src/backend_api/routes/v1/movies.py

git add apps/backend-api/
git commit -m "Update movies endpoint"

***REMOVED*** Output:
***REMOVED*** Backend API - Ruff Lint..................Passed
***REMOVED*** Backend API - Ruff Format................Passed
***REMOVED*** Backend API - Type Check.................Passed
```

Only 3 hooks run, not all 20+ hooks!

***REMOVED******REMOVED******REMOVED*** Example 2: Edit Multiple Apps

```bash
***REMOVED*** Edit files in two apps
git add apps/backend-api/ apps/auth-api/

git commit -m "Update auth and backend"

***REMOVED*** Output:
***REMOVED*** Backend API - Ruff Lint..................Passed
***REMOVED*** Backend API - Ruff Format................Passed
***REMOVED*** Backend API - Type Check.................Passed
***REMOVED*** Auth API - Ruff Lint.....................Passed
***REMOVED*** Auth API - Ruff Format...................Passed
***REMOVED*** Auth API - Type Check....................Passed
```

Only hooks for changed apps run!

***REMOVED******REMOVED******REMOVED*** Example 3: Edit Frontend

```bash
***REMOVED*** Edit Next.js file
git add apps/web-nextjs/src/app/page.tsx

git commit -m "Update homepage"

***REMOVED*** Output:
***REMOVED*** Web Next.js - ESLint.....................Passed
***REMOVED*** Web Next.js - Prettier...................Passed
```

***REMOVED******REMOVED******REMOVED*** Example 4: Edit Shared Library

```bash
***REMOVED*** Edit a shared library
git add libs/kafka/src/kafka/producer.py

git commit -m "Update Kafka producer"

***REMOVED*** Output:
***REMOVED*** Shared Libs - Ruff Lint..................Passed
***REMOVED*** Shared Libs - Ruff Format................Passed
```

***REMOVED******REMOVED*** Customizing Rules Per App

***REMOVED******REMOVED******REMOVED*** Python Apps

Edit `pyproject.toml` in each app:

**Stricter linting (e.g., for auth-api):**

```toml
[tool.ruff]
line-length = 88  ***REMOVED*** Stricter line length

[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "B",
    "S",   ***REMOVED*** flake8-bandit (security checks)
    "C90", ***REMOVED*** mccabe complexity
]
ignore = []  ***REMOVED*** No exceptions!

[tool.mypy]
python_version = "3.12"
strict = true  ***REMOVED*** Much stricter type checking
```

**Relaxed linting (e.g., for ml-api):**

```toml
[tool.ruff]
line-length = 120  ***REMOVED*** Longer lines allowed

[tool.ruff.lint]
select = ["E", "F"]  ***REMOVED*** Only errors and pyflakes
ignore = ["E501"]    ***REMOVED*** Ignore line length

[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = false  ***REMOVED*** Allow untyped functions
```

**Standard linting (default):**

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   ***REMOVED*** pycodestyle errors
    "W",   ***REMOVED*** pycodestyle warnings
    "F",   ***REMOVED*** pyflakes
    "I",   ***REMOVED*** isort
    "N",   ***REMOVED*** pep8-naming
    "UP",  ***REMOVED*** pyupgrade
    "B",   ***REMOVED*** flake8-bugbear
]
ignore = [
    "E501",  ***REMOVED*** line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  ***REMOVED*** Unused imports ok in __init__
"tests/**/*.py" = ["S101"]  ***REMOVED*** Asserts ok in tests

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

***REMOVED******REMOVED******REMOVED*** web-nextjs (JavaScript/TypeScript)

Edit `.eslintrc.json`:

```json
{
  "extends": ["next/core-web-vitals"],
  "rules": {
    "react-hooks/exhaustive-deps": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "no-console": "warn"
  }
}
```

Edit `.prettierrc`:

```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "avoid"
}
```

***REMOVED******REMOVED*** Bypassing Hooks

**Emergency only:**

```bash
git commit --no-verify
```

**When to use:**

- Critical production hotfix
- Known false positive that can't be fixed immediately
- CI/CD pipeline issue

**Better approach:** Fix the issues or adjust rules in the app's config.

***REMOVED******REMOVED*** Manual Hook Execution

***REMOVED******REMOVED******REMOVED*** Run all hooks on all files

```bash
pre-commit run --all-files
```

This is useful:

- After changing `.pre-commit-config.yaml`
- Before pushing to ensure everything passes
- After pulling changes from others

***REMOVED******REMOVED******REMOVED*** Run specific hook

```bash
***REMOVED*** Run only backend-api linting
pre-commit run backend-api-ruff-check --all-files

***REMOVED*** Run only formatting for auth-api
pre-commit run auth-api-ruff-format --all-files

***REMOVED*** Run web-nextjs ESLint
pre-commit run web-nextjs-eslint --all-files
```

***REMOVED******REMOVED******REMOVED*** Run hooks on specific files

```bash
***REMOVED*** Run hooks only on changed files
pre-commit run --files apps/backend-api/src/**/*.py

***REMOVED*** Run hooks on staged files (default behavior)
pre-commit run
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Hook fails for one app

```bash
***REMOVED*** Run the tool manually to see full error
cd apps/backend-api
ruff check .
mypy src/
```

***REMOVED******REMOVED******REMOVED*** Hook is slow

Some hooks may take time on first run due to:

- Installing tool environments
- Building caches

Subsequent runs are much faster due to pre-commit's caching.

***REMOVED******REMOVED******REMOVED*** Update hook definitions

After editing `.pre-commit-config.yaml`:

```bash
pre-commit install --install-hooks
```

***REMOVED******REMOVED******REMOVED*** Cache issues

```bash
***REMOVED*** Clear pre-commit cache
pre-commit clean

***REMOVED*** Reinstall everything
pre-commit uninstall
pre-commit install
```

***REMOVED******REMOVED******REMOVED*** Tool not found

If a hook fails with "command not found":

**For Python tools (ruff, mypy):**

```bash
pip install ruff mypy
```

**For web-nextjs tools:**

```bash
cd apps/web-nextjs
pnpm install
```

***REMOVED******REMOVED******REMOVED*** "Already installed" warning

If you see warnings about tools already being installed, this is normal and can be ignored.

***REMOVED******REMOVED*** Hook Configuration Reference

***REMOVED******REMOVED******REMOVED*** Available Hooks

**Backend API:**

- `backend-api-ruff-check` - Lint with auto-fix
- `backend-api-ruff-format` - Format code
- `backend-api-mypy` - Type checking

**Auth API:**

- `auth-api-ruff-check`
- `auth-api-ruff-format`
- `auth-api-mypy`

**BFF API:**

- `bff-api-ruff-check`
- `bff-api-ruff-format`

**Recommendation API:**

- `recommendation-api-ruff-check`
- `recommendation-api-ruff-format`

**Search API:**

- `search-api-ruff-check`
- `search-api-ruff-format`

**ML API:**

- `ml-api-ruff-check`
- `ml-api-ruff-format`

**Data Importer:**

- `data-importer-ruff-check`
- `data-importer-ruff-format`

**Web Next.js:**

- `web-nextjs-eslint` - ESLint with auto-fix
- `web-nextjs-prettier` - Prettier formatting

**Shared Libraries:**

- `libs-ruff-check` - Lint all libs/
- `libs-ruff-format` - Format all libs/

***REMOVED******REMOVED******REMOVED*** Hook Execution Flow

1. **Stage files:** `git add <files>`
2. **Commit:** `git commit -m "message"`
3. **Pre-commit runs:**
   - Checks which files changed
   - Runs only hooks matching those files
   - Auto-fixes issues where possible
   - Blocks commit if errors remain
4. **If hooks pass:** Commit succeeds
5. **If hooks fail:**
   - Commit is blocked
   - Review errors
   - Fix issues or stage auto-fixes
   - Try commit again

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** 1. Run hooks before committing

```bash
***REMOVED*** Check your changes before committing
pre-commit run
```

***REMOVED******REMOVED******REMOVED*** 2. Keep hooks fast

- Hooks should run in < 10 seconds
- If too slow, reduce scope or split hooks

***REMOVED******REMOVED******REMOVED*** 3. Auto-fix when possible

Most hooks auto-fix issues:

- Ruff formats code
- Prettier formats frontend
- Just stage and commit again

***REMOVED******REMOVED******REMOVED*** 4. Don't bypass hooks regularly

`--no-verify` should be rare. If you find yourself using it often:

- Rules may be too strict
- Consider adjusting config
- Discuss with team

***REMOVED******REMOVED******REMOVED*** 5. Update hooks regularly

```bash
***REMOVED*** Update pre-commit tool versions
pre-commit autoupdate
```

***REMOVED******REMOVED******REMOVED*** 6. Document custom rules

If you change linting rules for your app, document why in the `pyproject.toml`:

```toml
[tool.ruff.lint]
select = ["ALL"]  ***REMOVED*** Enable all rules
ignore = [
    "E501",  ***REMOVED*** Line too long - tables make this hard
    "S108",  ***REMOVED*** Hardcoded temp dir - intentional for tests
]
```

***REMOVED******REMOVED*** CI/CD Integration

Pre-commit hooks also run in CI/CD to catch issues that slip through:

```yaml
***REMOVED*** .github/workflows/lint.yml
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

***REMOVED******REMOVED*** Performance Tips

1. **Hooks only run on changed files** - Very fast!
2. **Caching** - Pre-commit caches tool environments
3. **Parallel execution** - Multiple hooks run in parallel where possible
4. **Skip unnecessary hooks** - File patterns ensure only relevant hooks run

***REMOVED******REMOVED*** Getting Help

If hooks are causing issues:

1. **Check the output** - Error messages are usually clear
2. **Run tool manually** - `cd app && ruff check .`
3. **Check config** - Look at app's `pyproject.toml`
4. **Ask the team** - Others may have seen the issue
5. **Update tools** - `pip install --upgrade ruff mypy`

***REMOVED******REMOVED*** Testing Your Setup

After setting up pre-commit, test that it works:

```bash
***REMOVED*** 1. Test backend-api hooks
cd apps/backend-api
echo "***REMOVED*** test" >> src/backend_api/__init__.py
git add src/backend_api/__init__.py
git commit -m "Test pre-commit"  ***REMOVED*** Should run backend-api hooks
git reset HEAD~1  ***REMOVED*** Undo test commit

***REMOVED*** 2. Test web-nextjs hooks
cd apps/web-nextjs
echo "// test" >> src/app/page.tsx
git add src/app/page.tsx
git commit -m "Test pre-commit"  ***REMOVED*** Should run web-nextjs hooks
git reset HEAD~1  ***REMOVED*** Undo test commit

***REMOVED*** 3. Test that unrelated apps don't trigger hooks
echo "***REMOVED*** test" >> README.md
git add README.md
git commit -m "Update README"  ***REMOVED*** No app-specific hooks should run
```

All tests should complete successfully, with only relevant hooks running for each test.
