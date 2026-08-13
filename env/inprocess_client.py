"""
In-Process HTTP-Compatible Client for the Mock Target Apps
============================================================

Training-speed optimization only — this does NOT change what is being
tested. It swaps the transport layer under WebSecurityGym's `self.session`
(real `requests.Session` over a real TCP socket) for Flask's built-in
`app.test_client()`, which calls straight into the same Flask routing /
view-function / response pipeline the real HTTP path uses. Same status
codes, same headers, same body content, same vulnerability behavior --
the only thing removed is the OS socket/TCP layer, which was pure
overhead relative to actual training signal.

Why this is safe to do:
- None of env/web_sec_env.py's actions depend on genuine network-timing
  side channels. The two `time.sleep(...)` calls in web_sec_env.py
  (attack_waf_timing_attack, action_wait) are both fixed artificial
  delays, not measurements of real response latency, so removing real
  network jitter does not change their behavior.
- Each of the 5 target apps uses its own separate SQLite file
  (env/banking.db, env/blog.db, env/ecommerce.db, env/fileshare.db,
  env/social.db) and its own Flask `app` instance, so importing all 5
  into one process is safe -- no shared global state to collide.

When NOT to use this:
- For the paper's final evaluation / results-table runs, keep using real
  HTTP via env/start_services.py + requests (WebSecurityGym's default
  session). The paper's contribution is framed as a black-box scanner
  interacting over HTTP; the in-process client is an internal training
  speed-up, not the methodology being evaluated. Mixing the two without
  saying so in the paper would be a real (if minor) integrity issue --
  don't.

Usage (see training/train_mock_targets.py --fast):
    from env.inprocess_client import build_target_sessions
    sessions = build_target_sessions()  # {port: InProcessSession}
    env = WebSecurityGym(target_url=url, mode="mock_targets",
                          session=sessions[port])
"""

from urllib.parse import urlparse

import requests
from requests.cookies import RequestsCookieJar


class _FakeRequest:
    """Minimal stand-in for requests.PreparedRequest -- .method and .body
    are the only attributes referenced anywhere in env/web_sec_env.py."""

    def __init__(self, method, body):
        self.method = method
        self.body = body


class _InProcessResponse:
    """Wraps a Flask test-client response to expose the subset of the
    requests.Response interface env/web_sec_env.py actually uses:
    .status_code, .text, .content, .headers, .url, .encoding, .request,
    ._content, .json().

    Mirrors real requests.Response's actual behavior (not just its
    attribute names): .text and .content are properties derived from
    ._content + .encoding, because at least one place in web_sec_env.py
    (the CTF-flag redaction path) mutates `response._content` directly
    and expects `.text` to reflect the change on next read -- exactly
    how requests.Response works internally. A version of this wrapper
    that stored .text/.content as plain fixed attributes would silently
    break that redaction.
    """

    def __init__(self, flask_response, request_url, request_method="GET", request_body=None):
        self._r = flask_response
        self.status_code = flask_response.status_code
        self.headers = flask_response.headers
        # .charset was removed from Werkzeug's Response class in newer
        # versions -- fall back to utf-8 (matches requests' own default)
        # rather than assuming the attribute exists.
        self.encoding = getattr(flask_response, "charset", None) or "utf-8"
        # requests.Response.url is the final (post-redirect) URL; the test
        # client doesn't follow redirects by default (matching the real
        # requests.Session calls elsewhere in this codebase, which also
        # don't pass allow_redirects), so the request URL is correct here.
        self.url = request_url
        self.request = _FakeRequest(request_method, request_body)
        try:
            self._content = flask_response.get_data()
        except Exception:
            self._content = b""
        # Per-response cookie jar attribute for interface parity; the
        # session-level jar (InProcessSession.cookies) is what actually
        # persists cookies across requests, matching requests.Session.
        self.cookies = RequestsCookieJar()

    @property
    def content(self):
        return self._content

    @property
    def text(self):
        try:
            return self._content.decode(self.encoding or "utf-8", errors="replace")
        except Exception:
            return ""

    def json(self):
        return self._r.get_json()


class InProcessSession:
    """Drop-in replacement for requests.Session that routes through a
    Flask app's test client instead of a real socket.

    Implements the subset of the requests.Session interface
    env/web_sec_env.py actually uses: .get, .post, .cookies
    (clear/get/set/copy, used directly by web_sec_env.py in several
    places), .headers (update/pop), and a no-op .mount for interface
    parity with the real-session setup path.
    """

    def __init__(self, flask_app):
        self._app = flask_app
        self._client = flask_app.test_client()
        self.cookies = RequestsCookieJar()
        self.headers = {}

    def mount(self, *args, **kwargs):
        # No-op: there is no real transport adapter to configure here.
        pass

    @staticmethod
    def _path_from_url(url):
        # web_sec_env.py builds full URLs like f"{self.target_url}/cart";
        # the test client only needs the path (+ query string).
        parsed = urlparse(url)
        path = parsed.path or "/"
        # Defensive: collapse a leading "//" (e.g. from
        # f"{target_url}/{item}" where item already starts with "/") down
        # to a single "/". Real HTTP servers tolerate a leading double
        # slash in a path; Werkzeug's test client does not -- it can
        # mis-parse the request when reconstructing the current URL and
        # raise a UnicodeError from an empty-hostname idna decode. Fixed
        # at the source in web_sec_env.py's attack_osint_files, but this
        # stays as a safety net against the same class of bug elsewhere.
        while path.startswith("//"):
            path = path[1:]
        if parsed.query:
            path += "?" + parsed.query
        return path

    def _merged_headers(self, extra):
        h = dict(self.headers)
        if extra:
            h.update(extra)
        cookie_dict = self.cookies.get_dict()
        if cookie_dict:
            h["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookie_dict.items())
        return h

    def _capture_cookies(self, flask_response):
        for raw in flask_response.headers.getlist("Set-Cookie"):
            first_pair = raw.split(";", 1)[0]
            if "=" in first_pair:
                k, v = first_pair.split("=", 1)
                self.cookies.set(k.strip(), v.strip())

    def get(self, url, timeout=None, headers=None, params=None, **kwargs):
        path = self._path_from_url(url)
        r = self._client.get(path, headers=self._merged_headers(headers), query_string=params)
        self._capture_cookies(r)
        return _InProcessResponse(r, url, "GET", None)

    def post(self, url, data=None, json=None, timeout=None, headers=None, files=None, **kwargs):
        path = self._path_from_url(url)
        body_for_request = json if json is not None else data
        if files:
            # Merge file fields into the form data for Werkzeug's test client.
            data = dict(data or {})
            data.update(files)
            r = self._client.post(path, data=data, headers=self._merged_headers(headers))
        else:
            r = self._client.post(
                path, data=data, json=json, headers=self._merged_headers(headers)
            )
        self._capture_cookies(r)
        return _InProcessResponse(r, url, "POST", body_for_request)

    def close(self):
        # Interface parity with requests.Session.close(), called from
        # WebSecurityGym.__del__. Nothing to release here -- the Flask
        # test client doesn't hold a real socket/connection.
        pass


# Port -> (module name, attribute) for the 5 mock target apps.
_TARGET_MODULES = {
    5002: "env.target_app_ecommerce",
    5003: "env.target_app_social",
    5004: "env.target_app_banking",
    5005: "env.target_app_blog",
    5006: "env.target_app_fileshare",
}


def build_target_sessions():
    """Imports all 5 mock target Flask apps into the current process and
    returns {port: InProcessSession}. Requires env/*.db files to already
    exist (run `python scripts/init_targets.py` once beforehand, same as for the
    real-HTTP path -- this function does not seed databases itself)."""
    import importlib
    import logging

    # Quiet Flask/Werkzeug's internal request-error logging. The agent
    # deliberately sends malformed requests as part of exploration (e.g.
    # a login POST with no password) -- the mock apps already handle this
    # correctly (return a 500, keep serving), and env/web_sec_env.py's own
    # step() has a broad except around every action so training/eval never
    # actually breaks because of it. But Flask's default error logger
    # prints a full traceback for every one of these caught exceptions,
    # which in a real training run means thousands of lines of "ERROR in
    # app: Exception on /api/login [POST]" burying real progress output
    # and making a perfectly healthy run look like it's stuck or crashing.
    # This does not hide anything that matters: the reward signal and
    # env-level "CRITICAL ERROR in Action X" messages are unaffected.
    logging.getLogger("werkzeug").setLevel(logging.CRITICAL)

    sessions = {}
    for port, module_path in _TARGET_MODULES.items():
        module = importlib.import_module(module_path)
        module.app.logger.setLevel(logging.CRITICAL)
        sessions[port] = InProcessSession(module.app)
    return sessions
