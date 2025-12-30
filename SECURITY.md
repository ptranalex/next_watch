## Security Policy

### Reporting a Vulnerability

If you discover a security issue, please **do not** open a public issue.

- **Preferred**: open a private security advisory in GitHub (Security → Advisories)
- **Alternative**: contact the maintainers via your preferred channel (if no email is published in package metadata)

### Repository Hygiene

- Never commit `.env` files, credentials, tokens, private keys, or data dumps.
- If secrets were committed, follow `docs/security/SECURITY_CLEANUP.md` and use `cleanup-git-history.sh` to rewrite history.
