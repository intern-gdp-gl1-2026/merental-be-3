Threat model: merental-be-3 (repository-grounded)

Scope
- In-scope: entire repository at /Users/admin/Desktop/intern/gdp/merental-be-3
- Excluded: tests/migrations/CI unless they affect runtime (none detected that change runtime behavior)
- Assumed runtime: backend web service exposed to the internet (user-provided). Where repo evidence contradicts an assumption, that is called out below.

Key repo evidence (examples)
- JWT issued in code: src/application/use_cases/user/login_user.py (jwt.encode using settings.SECRET_KEY) — line ~89
- JWT config: merentalbe3/settings.py lines ~131-133 (JWT_ALGORITHM = "HS256", JWT_EXPIRATION_HOURS = 24)
- SECRET_KEY comes from environment: merentalbe3/settings.py line 26 (SECRET_KEY = os.getenv("SECRET_KEY")) and is committed in .env -> /.env (contains SECRET_KEY and several API tokens)
- Database: merentalbe3/settings.py lines ~79-83 show SQLite: ENGINE = django.db.backends.sqlite3 and NAME = BASE_DIR / "db.sqlite3". A db.sqlite3 file exists at repository root (/Users/admin/Desktop/intern/gdp/merental-be-3/db.sqlite3)
- OpenAPI / endpoints: api/openapi.yml and api/paths/*.yml describing endpoints (auth_login, auth_register, reservations, users, cars, ping, etc.)
- URL routing: merentalbe3/urls.py includes admin and api (api url includes all API paths)
- Debug / host configuration: merentalbe3/settings.py DEBUG = True (line ~29) and ALLOWED_HOSTS = [] (line ~31)
- CSRF middleware present: merentalbe3/settings.py MIDDLEWARE includes "django.middleware.csrf.CsrfViewMiddleware" (line ~50)
- Cache used: merentalbe3/settings.py CACHES configured with LocMemCache (lines ~123-129)

Assumptions and conflicts
- User assumption: PostgreSQL. Repo evidence: SQLite (merentalbe3/settings.py lines 79-83) and a committed db.sqlite3 exists at repo root. Therefore the PostgreSQL assumption is incorrect for the repository as checked. Threat prioritization will mark any items that depend on DB type as conditional.
- User assumption: JWT-based authentication — supported by code and OpenAPI (see login_user.py and api/paths/auth_login.yml)
- User assumption: Public internet exposure — treat as true per scope request; no explicit WAF/ingress configs found in repo (no nginx/traefik/Kubernetes manifests present in repo root). If deployment adds a WAF reverse proxy the priority of some threats changes.
- Multi-tenancy: repository shows no multi-tenant controls; assume single-tenant unless customer corrects this.

System components (anchored to evidence)
- Django backend application (merentalbe3/settings.py, manage.py)
- Authentication module issuing JWTs (src/application/use_cases/user/login_user.py)
- HTTP API surface, OpenAPI contract (api/openapi.yml and api/paths/*.yml)
- SQLite local database (merentalbe3/settings.py; repository file db.sqlite3)
- Environment/secrets file (.env at repo root containing SECRET_KEY and third-party tokens)
- Local memory cache used for rate-limiting or caching (merentalbe3/settings.py CACHES: LocMemCache)
- Admin interface (Django admin in merentalbe3/urls.py path("admin/", ...))

Trust boundaries
- Internet -> HTTP API endpoints (api/openapi.yml, api/paths/*). Protocol: HTTP(S) (not enforced in repo). Boundary: unauthenticated vs authenticated endpoints.
- Authenticated API (JWT bearer tokens) -> application logic (login_user.py issues tokens; other endpoints require auth per OpenAPI references to Unauthorized/Forbidden responses in api/paths/*)
- Application -> Data store (application -> SQLite file db.sqlite3). Boundary: application enforces DB access control via Django ORM; physical file may be accessible if repository/host misconfigured.
- Application -> Third-party services (tokens present in .env for OpenAI, Cloudflare, Figma) — boundary: outbound API calls (no explicit usage found but tokens exist).
- Deployment boundary (repo -> production environment / reverse proxy) — no deployment manifests present; assume standard reverse proxy/host will be placed in front.

Assets
- Authentication secrets: SECRET_KEY (merentalbe3/settings.py + .env) — used for signing JWTs (src/application/use_cases/user/login_user.py)
- User credentials & PII: database file db.sqlite3 (repo root) and Django user models referenced in code and OpenAPI (api/paths/users.yml)
- JWT tokens (issued by login flow) and their signing keys
- Third-party API tokens (OpenAI, Cloudflare, Figma) in .env
- Source code and API contract (api/openapi.yml) — attackers can target endpoints listed there
- Admin interface access

Entry points (concrete files)
- POST /auth/login: api/paths/auth_login.yml (login operationId: loginUser)
- POST /auth/register: api/paths/auth_register.yml
- Reservations, users, cars API endpoints: api/paths/*.yml (several endpoints list Unauthorized/Forbidden responses)
- Django admin: /admin/ (merentalbe3/urls.py line 24)
- Any HTTP endpoint described in api/openapi.yml
- Local management commands via manage.py (admin tooling) — requires host access

Attacker capabilities (realistic, repository-anchored)
- Remote unauthenticated attacker able to send requests to documented endpoints (assume public internet exposure per scope).
- Attacker who has access to repository (or the repo is public) can read committed files like .env and db.sqlite3 (evidence: .env exists and contains secrets; db.sqlite3 is present in repo root). If repository were private, stolen credentials could still be obtained from a leaked copy.
- Attacker can craft JWTs if they obtain SECRET_KEY (login_user.py uses settings.SECRET_KEY to sign tokens).
- Attacker can attempt credential stuffing / brute-force login attempts (login endpoint exists; cache for rate limiting is LocMemCache which is ephemeral and not multi-instance safe).
- Local attacker with file system access to host can read db.sqlite3 or .env if file perms are weak — repo shows both files present.

Top abuse paths / prioritized threats (limited, high-quality)
1) Committed secrets + SECRET_KEY in .env -> token forging, third-party compromise (Priority: Critical)
   - Evidence: .env at repo root contains SECRET_KEY and other API tokens (/.env lines 1-4). login_user.py uses settings.SECRET_KEY to sign JWTs (src/application/use_cases/user/login_user.py line 89). JWT algorithm configured as HS256 in merentalbe3/settings.py line 132.
   - Attacker goal: impersonate arbitrary users, escalate privileges, or use third-party tokens to access external services.
   - Impact: High — attacker can mint valid JWTs (HS256 with known key) to bypass auth, access protected APIs, or act as admin; third-party keys enable broader compromise.
   - Likelihood: High if repository is accessible to attacker (evidence: secrets are committed). Even if repo is private, leaked snapshots make compromise likely.
   - Existing controls: SECRET_KEY is read from environment in settings.py (merentalbe3/settings.py line 26) — but committed .env defeats this control.
   - Recommended mitigations (concrete):
     1. Immediately rotate SECRET_KEY and all API tokens from .env (evidence: .env). Treat them as compromised.
     2. Remove .env from repository and add it to .gitignore. Purge secrets from git history (git filter-repo or BFG). See merentalbe3/settings.py which expects SECRET_KEY in environment.
     3. Use a secrets manager or encrypted environment variables at deploy time (e.g., Vault, cloud provider secrets). If continuing HS256, ensure SECRET_KEY is long and stored securely.
     4. Consider switching to asymmetric JWT signing (RS256) if multiple services need to verify tokens without sharing a symmetric secret; implement key loading from protected store and reference in login_user._generate_token.

2) db.sqlite3 committed in repo -> direct data exfiltration risk including user credentials and PII (Priority: High)
   - Evidence: db.sqlite3 exists at repository root (/Users/admin/Desktop/intern/gdp/merental-be-3/db.sqlite3) and DATABASES configured for sqlite in merentalbe3/settings.py lines ~79-83.
   - Attacker goal: extract user records, PII, hashed passwords, or session data; use extracted password hashes for offline cracking.
   - Impact: High for PII and credential theft; medium for availability.
   - Likelihood: High if repo is public or leaked; Moderate otherwise.
   - Existing controls: None visible that protect the committed database file.
   - Recommended mitigations (concrete):
     1. Remove db.sqlite3 from repository and add it to .gitignore. Purge from git history if necessary.
     2. If restoring DB is required for demos, provide sanitized dumps with no PII.
     3. Use production-grade DB (Postgres) managed securely and ensure DB dumps are never committed.

3) JWT signing + HS256 algorithm combined with SECRET_KEY exposure -> user impersonation (Priority: High)
   - Evidence: JWT signing in src/application/use_cases/user/login_user.py line 89 and JWT_ALGORITHM = "HS256" in merentalbe3/settings.py line 132. SECRET_KEY present in .env.
   - Attacker goal: manufacture valid tokens to access protected endpoints as arbitrary users.
   - Impact: High (complete auth bypass and unauthorized access to sensitive endpoints: reservations, users).
   - Likelihood: High if SECRET_KEY exposed; Low otherwise. Because .env contains secret, treat as High now.
   - Existing controls: token expiration set via JWT_EXPIRATION_HOURS = 24 (merentalbe3/settings.py line 133) reduces window but does not prevent forged tokens if key known.
   - Recommended mitigations (concrete):
     1. Rotate SECRET_KEY (see threat 1) and re-issue tokens.
     2. Consider RS256 with private key stored securely and public key for verification to avoid symmetric key sharing.
     3. Validate tokens with audience/issuer claims; include jti (token id) and maintain revocation list for compromised tokens.

4) Insecure default settings (DEBUG = True, ALLOWED_HOSTS = []) and missing HTTPS/cookie hardening -> information leakage / host header attacks (Priority: Medium-High)
   - Evidence: merentalbe3/settings.py DEBUG = True (line ~29) and ALLOWED_HOSTS = [] (line ~31). No SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, or HSTS settings present in settings.py.
   - Attacker goal: trigger detailed debug pages to leak secrets or stack traces; exploit host header poisoning when ALLOWED_HOSTS misconfigured in production.
   - Impact: Medium-High (sensitive internals, secrets could be exposed; host header attacks can poison cache or redirect flows).
   - Likelihood: Medium — depends on deployment; if DEBUG left enabled in production or ALLOWED_HOSTS left empty, likelihood increases.
   - Existing controls: CSRF middleware is enabled (merentalbe3/settings.py MIDDLEWARE includes CSRF middleware) which helps form-based CSRF, but API likely uses JWT.
   - Recommended mitigations (concrete):
     1. Ensure DEBUG=False in production and enforce via deployment checks (fail deployment if DEBUG True). See merentalbe3/settings.py currently sets DEBUG = True.
     2. Set ALLOWED_HOSTS via environment configuration and fail fast if empty in production.
     3. Enable SECURE_SSL_REDIRECT=True, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True and set HSTS headers in settings or deployment reverse proxy.

5) Rate limiting and caching setup insufficient for multi-instance or production deployments -> brute-force and DoS risks (Priority: Medium)
   - Evidence: merentalbe3/settings.py uses LocMemCache for CACHES (lines ~123-129). LocMemCache is per-process and not shared across instances. No explicit rate-limiting middleware or library found in repo.
   - Attacker goal: brute-force login or inventory endpoints; launch slow DoS by exhausting resources.
   - Impact: Medium (compromise of accounts via brute-force or service disruption).
   - Likelihood: Medium (depends on exposure and whether a production-grade rate-limiter is added at deployment). High if no external rate-limiter/WAF is present.
   - Existing controls: None explicit for global rate-limiting. API schemas include validation (OpenAPI) which helps reject malformed inputs.
   - Recommended mitigations (concrete):
     1. Add robust rate-limiting (e.g., Redis-backed throttling via Django REST framework throttling or middleware) that works across instances.
     2. Protect login endpoint (api/paths/auth_login.yml) with CAPTCHA challenges or progressive delays after repeated failures.
     3. Consider upstream rate limits or WAF rules for abusive IPs.

Cross-cutting observation: API contract visibility
- The repository contains a detailed OpenAPI contract (api/openapi.yml and api/paths/**). Publicly publishing this contract increases reconnaissance value to attackers by enumerating entry points and expected request shapes. Hardening should be focused on endpoints that operate on sensitive assets (users, reservations).

Existing controls vs recommended mitigations (summary)
- Existing controls (evidence):
  - JWT expiration configured (merentalbe3/settings.py JWT_EXPIRATION_HOURS = 24)
  - CSRF middleware present (merentalbe3/settings.py MIDDLEWARE)
  - Input schema documented in OpenAPI (api/paths/*.yml) which helps validation
  - SECRET_KEY is loaded from environment in settings.py (merentalbe3/settings.py line 26) — good pattern but broken by committed .env
- Recommended mitigations (concrete, prioritized):
  1. Secrets & keys: rotate immediately, remove .env from repo, purge history, use secure secrets manager. (High priority)
  2. Remove committed db.sqlite3 from repo, purge history, and move to a managed DB for production. (High priority)
  3. Harden JWT practices: consider RS256, audience/issuer/jti, revocation support, shorter lifetimes for access tokens with refresh tokens. (High priority)
  4. Production settings guardrails: enforce DEBUG=False at deploy, require ALLOWED_HOSTS configured, enable secure cookie settings and HSTS. (High priority)
  5. Add cross-instance rate-limiting (Redis-based) and protect login endpoints with progressive delays/CAPTCHA. (Medium priority)
  6. Review OpenAPI publication policies: if API spec must remain private, do not publish it in public repo or redact sensitive details.

Likelihood / impact reasoning notes (qualitative)
- The single dominant factor raising likelihood across several threats is the presence of committed secrets (.env) and db.sqlite3. When secrets/data are committed, abuse paths like token forging and data exfiltration move from speculative to likely.
- If deployment includes a secure reverse proxy, WAF, and secrets are rotated, likelihood for some threats (token forging, brute-force DoS) reduces; these mitigations should be applied in deployment pipelines.

Conditional statements
- The user's initial assumption of PostgreSQL is not reflected by repository contents: repo uses SQLite (merentalbe3/settings.py lines ~79-83 and db.sqlite3 present). Any recommendations tied specifically to Postgres (e.g., managed RDS encryption) are therefore conditional and not applied directly here.
- If this code will be deployed in a multi-instance production environment, several priorities change (e.g., LocMemCache becomes a clear control gap for cross-instance rate limiting).

Open questions (please confirm)
1) Is the deployed production environment different from repository (e.g., will you use PostgreSQL, external secrets manager, and a reverse proxy/WAF)? If so, which components will be used (Postgres provider, secret manager, proxy)?
2) Is the OpenAPI contract intended to be public or private in your deployment (i.e., will it be published for public consumers)?

If you cannot or will not answer, I will treat the repo-as-is (secrets and sqlite committed) as the ground truth and keep the threat prioritization as stated.

Deliverables
- This threat model (file): output/security-threat-model/merental-be-3-threat-model.md (this file)
- Evidence references: file paths are included throughout the report for traceability.

End of report.
