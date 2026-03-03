# Security Best Practices Report

Repository: merental-be-3
Path: /Users/admin/Desktop/intern/gdp/merental-be-3

Executive Summary
-----------------
Primary language: Python
Primary frameworks/libraries: Django (>=5.0), django-ninja (FastAPI-like router), PyJWT, bcrypt, python-dotenv

This report prioritizes highest-impact security findings (auth, secrets, injection, access control, insecure defaults) and provides file-level citations with line numbers. Focus is on issues that allow account compromise, secret leakage, authentication bypass, insecure defaults in production, and common injection vectors.

Severity Legend
---------------
- CRITICAL: Immediate action required; secrets or settings allowing full compromise.
- HIGH: High impact vulnerabilities that allow impersonation, privilege escalation, or data exposure.
- MEDIUM: Security issues that reduce defense-in-depth or enable attacks under some conditions.
- LOW: Best-practice improvements, hardening, or informational findings.

Findings
--------

CRITICAL
--------

CRIT-001: Secrets committed to repository (.env contains SECRET_KEY and third-party API keys)
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/.env
    - Line 1: SECRET_KEY=django-insecure-u2w2pz_k)97h3l$)b92^lz!ltsx$le(!f18&6&3%nxb9_2-ihm
    - Line 2: OPENAI_API_KEY="sk-proj-..."
    - Line 3: CLOUDFLARE_API_TOKEN="K4-wsX8X6N49EmfHV1mY74H4ck-v5tSq5qvHjgrK"
    - Line 4: FIGMA_OAUTH_TOKEN="figd_..."
- Why critical: The Django SECRET_KEY is used for signing cookies and JWTs (see HIGH-004). API keys and tokens provide direct access to external services. Committed secrets in a repo are immediate compromise vectors.
- Remediation (immediate):
  1. Rotate all secrets immediately (SECRET_KEY, OpenAI key, Cloudflare token, Figma token). Treat them as compromised.
  2. Remove .env from the repository and add it to .gitignore. Purge secrets from repository history if feasible (git filter-repo or BFG).
  3. Move secrets to a secure secrets manager (AWS Secrets Manager, HashiCorp Vault, or environment variables injected by CI/CD).

HIGH
----

HIGH-001: DEBUG mode enabled in settings (unsafe for production)
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/merentalbe3/settings.py
    - Line 29: DEBUG = True
- Why high: DEBUG=True can leak sensitive information (stack traces, settings, environment variables) to attackers if exposed in production.
- Remediation:
  1. Ensure DEBUG is False in production. Use environment variables to control DEBUG.
  2. Configure proper logging and error reporting (Sentry) for production.

HIGH-002: ALLOWED_HOSTS empty (allows Host header attacks in production)
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/merentalbe3/settings.py
    - Line 31: ALLOWED_HOSTS = []
- Why high: Empty ALLOWED_HOSTS is acceptable in dev with DEBUG True, but in production this must be set to prevent host header poisoning.
- Remediation:
  1. Set ALLOWED_HOSTS to the list of allowed hostnames in production.

HIGH-003: LocMemCache used for rate-limiting cache (not suitable for multi-process production)
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/merentalbe3/settings.py
    - Lines 124-129: CACHES configured with 'django.core.cache.backends.locmem.LocMemCache'
- Why high: Rate-limiting uses django-ratelimit which relies on cache backend. LocMemCache is per-process and won't coordinate across worker processes, allowing attackers to bypass rate limits.
- Remediation:
  1. Use a shared cache backend (Redis, Memcached) for rate-limiting in production.

HIGH-004: JWT signing uses SECRET_KEY (HS256) and secret is exposed
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/src/application/use_cases/user/login_user.py
    - Line 89: token = jwt.encode(payload, settings.SECRET_KEY, algorithm=algorithm)
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/.env
    - Line 1: SECRET_KEY=django-insecure-...
- Why high: With SECRET_KEY exposed (CRIT-001), an attacker can forge HS256 tokens and impersonate users or escalate privileges.
- Remediation:
  1. Rotate SECRET_KEY immediately.
  2. Consider using asymmetric JWT (RS256) with private key in a secure store for signing.
  3. Validate tokens server-side with strict verification and consider audience (aud) and issuer (iss) claims.

MEDIUM
------

MED-001: No token revocation or refresh strategy implemented
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/src/application/use_cases/user/login_user.py
    - Lines 75-90: _generate_token generates JWT with exp and iat, no refresh or revocation hooks.
- Why medium: Long-lived tokens (24 hours by default) can be abused if leaked; no revocation prevents session invalidation on credential compromise.
- Remediation:
  1. Implement short-lived access tokens and refresh tokens with rotation and revocation lists (store refresh tokens server-side or use JWT with jti and server-side blocklist).
  2. Reduce default JWT_EXPIRATION_HOURS in settings for production.

MED-002: No authorization checks on resource endpoints
- Evidence:
  - Files: /Users/admin/Desktop/intern/gdp/merental-be-3/src/api/regionals.py and /src/api/cars.py
    - Example: create_regional (line 31), create_car (lines 64-84) do not check authenticated user or permissions.
- Why medium: Endpoints appear public and allow creation, update, delete operations without authentication/authorization, enabling unauthorized changes.
- Remediation:
  1. Enforce authentication middleware for API routes and require tokens in Authorization header.
  2. Implement role-based access control or ownership checks for sensitive operations.
- Note: The project has JWT issuance but no middleware shown verifying tokens on requests.

MED-003: Password storage field allows arbitrary text; ensure hashing is always used
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/src/infrastructure/models/user_model.py
    - Line 6: password = models.TextField()
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/src/infrastructure/repositories/django_user_repository.py
    - Line 28: user_model = UserModel(username=user.username, password=user.password)
- Why medium: TextField is fine but repository trusts caller to always hash; ensure there are checks to prevent raw password storage.
- Remediation:
  1. Enforce password hashing at model save or use Django's built-in User model which enforces password hashing.
  2. Add unit tests or assertions to ensure stored passwords are bcrypt hashes (e.g., prefix $2b$).

LOW
---

LOW-001: CSRF middleware enabled but API uses token auth - ensure CSRF exempt for token endpoints if appropriate
- Evidence:
  - File: /Users/admin/Desktop/intern/gdp/merental-be-3/merentalbe3/settings.py
    - Line 50: "django.middleware.csrf.CsrfViewMiddleware"
  - Files: API endpoints implemented via django-ninja which typically require CSRF exemption for token-based auth.
- Why low: Potential mismatch between CSRF protections and token-based API endpoints; may require configuring CSRF exemption for JSON APIs.
- Remediation:
  1. Configure CSRF exemptions for API endpoints authenticated via tokens, and ensure safe defaults for browser-exposed endpoints.

LOW-002: ALLOWED_HOSTS and other security settings (SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE) not configured
- Evidence:
  - Settings file lacks SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE.
- Why low: Hardening settings are recommended in production.
- Remediation:
  1. Enable SECURE_SSL_REDIRECT, set SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True, and configure HSTS.

Appendix: Important file references
---------------------------------
- /Users/admin/Desktop/intern/gdp/merental-be-3/.env (lines 1-4)
- /Users/admin/Desktop/intern/gdp/merental-be-3/merentalbe3/settings.py (lines 20-33, 124-133)
- /Users/admin/Desktop/intern/gdp/merental-be-3/src/application/use_cases/user/login_user.py (lines 75-90)
- /Users/admin/Desktop/intern/gdp/merental-be-3/src/application/use_cases/user/register_user.py (lines 81-90)
- /Users/admin/Desktop/intern/gdp/merental-be-3/src/infrastructure/models/user_model.py (lines 4-7)
- /Users/admin/Desktop/intern/gdp/merental-be-3/src/infrastructure/repositories/django_user_repository.py (lines 14-31)
- /Users/admin/Desktop/intern/gdp/merental-be-3/src/api/users.py (lines 17-58)

End of report.
