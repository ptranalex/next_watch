# Public Repo Safety Checklist

Use this checklist **before** switching the repository visibility to public.

## Working tree (current files)

- [ ] Confirm no real `.env*` files are tracked (only `*.example` templates)
  - `git ls-files | grep -E '(^|/)\\.env(\\..*)?$'`
- [ ] Confirm no DB dumps / local data files are tracked
  - `git ls-files | grep -E '\\.(db|sqlite|sqlite3)$'`
- [ ] Confirm no private keys / certs are tracked
  - `git ls-files | grep -E '\\.(pem|key|p12|pfx)$|(^|/)id_rsa'`
- [ ] Confirm there is no personal data you don’t want public (emails/domains/usernames)

## Git history (past commits)

- [ ] Run the history cleanup script if secrets were ever committed:
  - `./cleanup-git-history.sh /path/to/replacements.txt`
  - replacements format: `<literal-to-find>==><replacement>`
- [ ] Verify the cleaned repo no longer contains the sensitive paths/strings

## Automation (prevent regressions)

- [ ] Ensure secret scanning is enabled in CI:
  - GitHub Actions workflow: `.github/workflows/secret-scan.yml`

## After making public

- [ ] Rotate/revoke anything that might have been exposed (tokens, passwords, OAuth creds, JWT secrets, internal API keys)
- [ ] Ask existing collaborators to re-clone if you rewrote history
