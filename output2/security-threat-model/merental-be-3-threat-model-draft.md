Threat model for repository: /Users/admin/Desktop/intern/gdp/merental-be-3

Summary of concrete evidence (anchors)
- Django settings: merentalbe3/settings.py
  - SECRET_KEY loaded from .env: settings.py line 20-26 (SECRET_KEY = os.getenv("SECRET_KEY"))
  - DEBUG = True (settings.py line 29)
  - ALLOWED_HOSTS = [] (settings.py line 31)
  - JWT config present: JWT_ALGORITHM = "HS256", JWT_EXPIRATION_HOURS = 24 (settings.py lines 131-133)
  - Database configured as SQLite: DATABASES -> ENGINE = django.db.backends.sqlite3, NAME = BASE_DIR / "db.sqlite3" (settings.py lines 79-83)
  - Cache: LocMemCache configured (settings.py lines 123-129)

- .env present in repo root with secrets (file: .env)
  - SECRET_KEY value present (file includes SECRET_KEY=django-insecure-...)
  - Several API tokens present (OPENAI_API_KEY, CLOUDFLARE_API_TOKEN, FIGMA_OAUTH_TOKEN) (see .env)

- Authentication & token generation evidence
  - Login use case generates JWT using settings.SECRET_KEY: src/application/use_cases/user/login_user.py (lines 75-90)
  - JWT payload contains user_id, username, exp, iat and uses jwt.encode with settings.SECRET_KEY and settings.JWT_ALGORITHM
  - Password hashing & verification uses bcrypt: src/application/utils/password_utils.py (hash_password and verify_password)
  - User entity enforces strong password requirements on registration: src/domain/entities/user.py (password validation logic lines 56-72)
  - UserModel stores password in database (TextField): src/infrastructure/models/user_model.py (password = models.TextField())
  - User repository saves/loads users: src/infrastructure/repositories/django_user_repository.py (saves plain hashed password to UserModel)

- API surface (entry points)
  - API router registration: merentalbe3/api.py (api.add_router "/auth", "/regional", "/cars")
  - Auth endpoints: src/api/users.py (POST /auth/register, POST /auth/login) with django-ratelimit decorators and explicit rate limits
  - Regional endpoints: src/api/regionals.py (CRUD endpoints with rate limits)
  - Cars endpoints: src/api/cars.py (CRUD endpoints)
  - Admin interface mounted at /admin: merentalbe3/urls.py

- Other relevant notes
  - Rate limiting decorator used: django_ratelimit.decorators.ratelimit in src/api/users.py and src/api/regionals.py
  - Rate limit cache backend is LocMemCache -> settings.py
  - There is no visible middleware or code that enforces JWT validation or authorization checks on API endpoints (no references to verifying JWT or checking request.user in src/api/* files)
  - README minimal

Assumptions (explicit)
- User requested assumptions: public internet exposure, JWT-based authentication, PostgreSQL; however repository shows SQLite in settings.py (settings.py lines 79-83). I will treat PostgreSQL as a deployment-time choice; where assumptions differ from repo evidence I will mark conditional prioritization.
- No WAF detected in repo (no nginx/ingress/Kubernetes manifests); treat presence of WAF as "not visible in repo; verify at runtime/config".
- Single-tenant unless repo shows multi-tenancy (no multi-tenant code found).

System components (anchored)
- Web application (Django + Ninja API): merentalbe3/api.py, merentalbe3/urls.py
- API handlers (business logic layers): src/api/*.py (users.py, regionals.py, cars.py)
- Application use-cases (domain logic): src/application/use_cases/* (login_user.py, register_user.py, car use cases, regional use cases)
- Repositories / persistence adapters (Django ORM models): src/infrastructure/repositories/* and src/infrastructure/models/* (UserModel, CarModel, RegionalModel)
- Configuration & secrets: .env and merentalbe3/settings.py
- Local cache backend used for rate limiting: LocMemCache (settings.py)
- Admin UI: /admin (merentalbe3/urls.py)

Trust boundaries
- Public internet <-> Django/Ninja API (merentalbe3/api.py) — untrusted external callers
- API <-> Database (SQLite by repo; intended Postgres in deployment) — boundary for persistent data
- Application code <-> external services (OpenAI, Cloudflare, Figma) using tokens in .env
- Admin interface (/admin) boundary: administrative users vs public

Assets
- Authentication secrets: SECRET_KEY (.env) — used to sign JWTs (login_user.py line 89)
- User credentials (hashed passwords) stored in DB: src/infrastructure/models/user_model.py
- JWT tokens issued to users (usable for session/auth): produced in login_user.py
- Application data: Cars, Regionals stored in models CarModel, RegionalModel
- Third-party API tokens in .env (OPENAI_API_KEY, CLOUDFLARE_API_TOKEN, FIGMA_OAUTH_TOKEN)
- Source code and configuration (repo) including .env (sensitive)

Entry points (observable)
- /auth/register (POST) — src/api/users.py (rate-limited 5/m) — accepts username/password/confirmPassword
- /auth/login (POST) — src/api/users.py (rate-limited 10/m) — returns JWT token on success
- /cars (GET, POST, PUT, DELETE) — src/api/cars.py (CRUD)
- /regional (GET, POST, PUT, DELETE) — src/api/regionals.py (CRUD)
- /ping (GET) — merentalbe3/api.py
- /admin/ — Django admin site — merentalbe3/urls.py

Attacker capabilities (assumed from public exposure + code)
- Can access any public endpoint (register, login, cars, regional, ping, admin UI) over the internet.
- Can read repository if attacker has repo access (evidence: .env in repo contains secrets) — immediate secret compromise.
- Can attempt brute-force or credential stuffing against /auth/login; rate limit exists but is LocMemCache-backed and may not be effective across multiple processes or in distributed deployments.
- Can attempt to create or modify cars/regionals via API endpoints; code does not show authentication/authorization checks.
- Can attempt to forge JWTs if SECRET_KEY is known (login_user.py uses settings.SECRET_KEY for HS256 signing).

High-quality, prioritized threats (limited set)
1) Secret exposure (committed .env with SECRET_KEY and API tokens)
   - Evidence: .env file at repository root contains SECRET_KEY and other tokens (./.env)
   - Why it matters: SECRET_KEY enables JWT signing and potentially Django session forgery; API tokens allow attackers to access third-party services and escalate impact.
   - Likelihood: High (observed in repo)
   - Impact: Critical (full account/session forgery, third-party abuse, supply-chain exposure)
   - Existing controls: SECRET_KEY is read from .env (settings.py line 20) but no gitignore or removal — actual secret is committed
   - Recommended mitigations (priority):
     - Remove .env from repository, rotate all exposed secrets immediately (SECRET_KEY, OPENAI_API_KEY, etc.).
     - Move secrets to an external secrets manager (AWS Secrets Manager, Vault, etc.) and load at runtime.
     - Add .env to .gitignore and perform a git history purge if secrets were committed (BFG or git filter-repo).
     - Short-term: rotate tokens and secret used to sign JWTs.

2) Missing authentication/authorization enforcement on API endpoints
   - Evidence: src/api/* handlers (cars.py, regionals.py, users.py) do not validate JWTs or check request.user; login_user.py issues JWT but no code to verify/enforce it is visible in API layer.
   - Why it matters: If endpoints are not protected, any unauthenticated user can create/update/delete resources (cars, regionals) or access data that should be restricted.
   - Likelihood: High (observed in code)
   - Impact: High (data integrity loss, privacy breach, unauthorized modifications)
   - Existing controls: None visible in repo (no JWT auth middleware or decorator usage)
   - Recommended mitigations:
     - Implement JWT verification middleware or use Ninja/Django authentication backends to require Authorization: Bearer <token> and validate tokens (e.g., add a dependency that checks and injects current user into request).
     - Mark endpoints that must be protected and enforce role-based checks where appropriate.
     - Add integration tests to verify unauthorized requests are rejected.

3) Token forging and session takeover due to symmetric signing key exposure and HS256 usage
   - Evidence: JWT is signed with settings.SECRET_KEY using HS256 (login_user.py line 89, settings.py lines 26, 131)
   - Why it matters: If SECRET_KEY is leaked (see threat 1) or weak, attacker can forge JWTs to impersonate users; HS256 uses symmetric keys which require extra care to keep secret.
   - Likelihood: Medium-High (conditional on secret exposure; .env shows SECRET_KEY leaked)
   - Impact: High (account takeover, privilege escalation)
   - Existing controls: JWT expiration (24 hours) present (settings.py line 133)
   - Recommended mitigations:
     - Rotate SECRET_KEY and avoid committing it to repo.
     - Consider using asymmetric JWT (RS256) with private key stored securely and public key deployed to verification services.
     - Reduce token lifetime and add refresh token rotation, and implement token revocation/blacklist for critical events (password reset, logout).
     - Log and monitor suspicious token usage.

4) Ineffective rate limiting and brute-force / DoS risk (LocMemCache)
   - Evidence: Rate-limiting decorators on endpoints (src/api/users.py lines 21,45 and src/api/regionals.py lines 30,97,125) but cache backend is LocMemCache (settings.py lines 123-129).
   - Why it matters: LocMemCache is per-process memory cache. In multi-process deployments (gunicorn, multiple containers) or horizontally scaled environments, rate limits won't be shared; attackers can bypass limits by sending requests to multiple instances. Also LocMemCache is lost on restart.
   - Likelihood: Medium (depends on deployment), High if deployed multi-process without shared cache
   - Impact: Medium-High (brute-force credential guessing, account enumeration, API abuse, DoS)
   - Existing controls: Rate limit decorators present; comment in code mentions X-Forwarded-For header handling note (src/api/users.py lines 25-26)
   - Recommended mitigations:
     - Use a centralized cache/store for rate limiting (Redis) configured as Django cache backend.
     - Add upstream deployment controls: reverse proxy rate-limits, WAF rules, CDN protections.
     - Implement account lockout or adaptive throttling on failed login attempts.

5) Debug/host configuration and information exposure
   - Evidence: settings.py DEBUG = True (line 29), ALLOWED_HOSTS = [] (line 31)
   - Why it matters: DEBUG True can leak stack traces and sensitive data in error pages; ALLOWED_HOSTS empty may allow host header attacks in certain setups.
   - Likelihood: Medium (observed in repo, but may be a development setting not used in production)
   - Impact: Medium (information disclosure enabling easier exploitation)
   - Existing controls: None visible for production hardening
   - Recommended mitigations:
     - Ensure DEBUG=False in production and set ALLOWED_HOSTS to production hostnames.
     - Use environment-specific settings and check in deployment pipelines to prevent accidental DEBUG=True in prod.

6) Admin interface exposure and weak protection
   - Evidence: Django admin mounted at /admin (merentalbe3/urls.py lines 23-25). No admin-specific hardening visible.
   - Why it matters: Admin interfaces are high-value targets; without IP restrictions, MFA, or separate admin networks, they can be brute-forced or exploited.
   - Likelihood: Medium (admin interface present)
   - Impact: High (full data control if admin compromised)
   - Existing controls: None seen in repo
   - Recommended mitigations:
     - Protect /admin with IP whitelisting, VPN, or at minimum enforce strong auth (MFA) and unique admin credentials.
     - Consider moving admin interface to an internal-only network or obscuring it behind a management plane.

Other analysis notes
- SQL injection risk: Low — code uses Django ORM and parameterized queries (models, .objects.get/filter), lowering risk of raw-SQL injection. Re-check if any raw SQL is added in other parts of repo.
- Password storage: Good — bcrypt used for hashing (src/application/utils/password_utils.py). Password strength checks enforced in domain model (src/domain/entities/user.py).
- Logging: Some error logging in repositories (logger.error calls) but care should be taken not to log secrets. E.g., django_user_repository logs DatabaseError message (could inadvertently contain sensitive data) — src/infrastructure/repositories/django_user_repository.py line ~53.

Priority and conditional notes
- The highest-priority immediate action is secret rotation and removing .env from repo (Threat 1) because it materially increases the risk of other threats (token forging, third-party service abuse).
- Missing authentication enforcement (Threat 2) is critical and independent — if the app is intended to be protected by JWTs, code currently lacks enforcement. If the deployment includes an API gateway that enforces auth (not visible in repo), this reduces priority; mark as conditional: "priority high unless a runtime gateway enforces authentication/authorization." (No WAF/gateway manifests found in repo)

Deliverables
- This draft threat model (this file) anchored to repository evidence.

Clarification questions (1-3) — required before finalizing the report
1) Will production use PostgreSQL and an external secrets manager (e.g., Vault, AWS Secrets Manager), or do you plan to deploy using the current settings.py (SQLite and .env)?
2) Are the API endpoints intended to be protected by JWTs (i.e., should authenticated requests be required for cars/regional CRUD), or is there an external gateway that performs authentication/authorization before requests reach this app?

If either assumption is incorrect, I will mark threat prioritization as conditional and update the final report accordingly.


-- End of draft
