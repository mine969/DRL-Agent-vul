
## Global fixes for mock websites (all 5 apps)

* **Ensure `env/` exists** before opening DBs: `os.makedirs("env", exist_ok=True)`
* **Consistent session fields**
  * Always store: `session["user_id"] = int`
  * Always store: `session["username"] = str`
  * Don’t mix `username` string into `user_id`.
* **Add missing imports**
  * Example: Blog SSRF uses `requests` but not imported.
* **Make DB connections safe**
  * Use parameterized queries everywhere *except* the intentional SQLi endpoints.
* **Avoid duplicate routes**
  * In Social app you define `/api/messages/<user_id>` twice (one without JWT and one with JWT). Flask will override one -> unpredictable.

---

## Variant 2 — Social Media (Research Variant 2, port 5003)

### Critical “it will break / behave wrong”

1. **Duplicate route: `/api/messages/<user_id>`**
   * You have it twice:
     * `get_messages_api(user_id)` (no JWT)
     * `api_messages(user_id)` (JWT + decorator)
   * Fix: rename one endpoint path, e.g.:
     * `/api/messages/<user_id>` (JWT)
     * `/api/public/messages/<user_id>` (unsafe training)
2. **Unreachable code in `/login`**
   * You do `return add_security_headers(response)` then later:
     <pre class="overflow-visible! px-0!" data-start="1488" data-end="1577"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-py"><span><span>session[</span><span>'username'</span><span>] = user[</span><span>'username'</span><span>]
     </span><span>return</span><span> redirect(</span><span>'/posts'</span><span>)
     </span></span></code></div></div></pre>
   * That block never runs. Remove it.
3. **Session type mismatch**
   * In register you set `session['user_id'] = username` (string)
   * In login you set `session['user_id'] = user['id']` (int)
   * Fix: after registration, fetch created user id, then store int.
4. **JWT decorator stores request.user_id but code sometimes uses session**
   * You mix JWT auth and session auth routes. That’s fine, but be consistent per endpoint.
   * Fix: endpoints under `/api/...` should use JWT OR session, not both randomly.

### Research-quality improvements (still vulnerable, but cleaner)

5. **Rate limit memory leak**
   * `request_counts` dict grows forever for new IPs.
   * Add periodic cleanup or cap size.
6. **CSRF token store is global dict**
   * If you restart app tokens vanish; also you key by `session_id` which may be `anonymous`.
   * For research apps this is OK, but fix by ensuring session_id always exists for token routes.
7. **File upload serving bug potential**
   * `send_from_directory(UPLOAD_FOLDER, filename)` is ok, but your comment says traversal — Werkzeug generally normalizes.
   * If you *want* traversal vulnerability, you need to intentionally implement unsafe path join + `open()`.
   * If you *don’t want* traversal, keep `send_from_directory` and remove the comment.

---

## Variant 3 — Banking (Research Variant 3, port 5004)

1. **CSRF bypass logic is fine, but token generation isn’t wired**
   * You generate CSRF tokens in helper but  **dashboard quick transfer form has no csrf_token field** .
   * If you want “sometimes protected sometimes bypassable”, do:
     * dashboard form includes CSRF token
     * `/transfer` accepts missing token (vuln)
   * Right now it’s basically always missing.
2. **Account route renders unsafe f-string HTML**
   * You build HTML with f-string and insert DB fields directly.
   * That creates accidental XSS everywhere even if you didn’t intend it.
   * Fix: use Jinja template rendering and pass variables.
3. **Rate limit dict grows forever**
   * Same as social: add cleanup.

---

## Variant 4 — Blog (Research Variant 4, port 5005)

1. **Missing import**
   * `requests` is used in SSRF route but not imported → app will crash.
2. **OIDC “alg:none” logic may crash depending on pyjwt**
   * `jwt.encode(... algorithm=None)` behavior differs across versions.
   * Safer: manually craft a “none” JWT for the challenge, or use pyjwt calls with explicit options.
   * Fix goal: make it deterministic across environments.
3. **Home page template mixing**
   * Your `HOME_PAGE` uses `{% for post in posts %}` but in some branches you replace parts and then cut template strings.
   * This can easily cause broken rendering.
   * Fix: keep one consistent Jinja template and pass flags/messages via variables.

---

## Variant 1 / Variant 5 / Variant “Fileshare”

You didn’t paste those here, so I can’t point exact line-level bugs, but these are the most common issues I’d check in them:

* duplicate routes
* missing imports
* DB path issues
* inconsistent session usage
* unreachable code after return
* API endpoints mixing session + JWT inconsistently
* accidental vuln leakage (XSS everywhere) due to f-string HTML rendering

If you paste **just the top-level route list** (`@app.route(...)`) for those 2 remaining files, I can sanity-check for duplicates and missing endpoints without needing all code.
