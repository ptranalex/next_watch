***REMOVED*** Security Cleanup (Redacted)

This document intentionally **does not** include any real credentials, API keys, passwords, domains, or personal data.

***REMOVED******REMOVED*** Why this exists

- **Goal**: keep the *process* for security cleanup documented, without ever storing secrets in git.
- **Rule**: never commit `.env` files, API keys, passwords, tokens, private keys, or “incident reports” that embed them.

***REMOVED******REMOVED*** If secrets were committed

1. **Remove secrets from the current working tree**
   - Delete any committed secret files (e.g. `.env`, exported credentials, DB dumps).
2. **Rewrite git history**
   - Use the repo’s `cleanup-git-history.sh` script to remove sensitive files from all commits/tags.
3. **Force push rewritten history**
   - Only after you’ve validated the cleanup locally.
4. **Rotate everything that was exposed**
   - API keys/tokens, admin passwords, JWT secrets, internal API keys, OAuth credentials, etc.
5. **Verify + monitor**
   - Re-deploy with new secrets and watch logs/alerts for unexpected usage.

***REMOVED******REMOVED*** Local-only notes

If you need to keep a detailed internal report, store it outside git or under a gitignored folder such as `docs/internal/`.
