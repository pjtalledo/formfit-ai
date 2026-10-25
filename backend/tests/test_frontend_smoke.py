"""
Real, headless-browser smoke test for the frontend. This exists specifically
because an HTTP 200 response from the static file server is NOT sufficient
evidence the UI actually works — a real bug shipped where the page returned
200 and showed the header, but React never mounted (see docs/TECHNICAL_AUDIT.md
"Frontend Blank Page Fix"). This test renders the real page in headless
Chromium via Playwright and asserts on the actual DOM, not just the HTTP
status code.

Requires `playwright` + a downloaded Chromium build (`playwright install
chromium`). Skipped (not failed) if Playwright or its browser isn't
available, so this doesn't break environments where it wasn't installed —
but a skip must never be read as a passing UI check.
"""
import socket
import threading
import time

import pytest
import uvicorn

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

requires_playwright = pytest.mark.skipif(
    not PLAYWRIGHT_AVAILABLE, reason="playwright not installed — skipping real-browser smoke test"
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture()
def live_server(test_db, monkeypatch):
    """Runs the real FastAPI app (with an isolated test DB) on a free port."""
    from app.main import app
    from app import database as db_module

    def _override_get_db():
        yield test_db

    app.dependency_overrides[db_module.get_db] = _override_get_db

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)
    app.dependency_overrides.clear()


@requires_playwright
def test_frontend_actually_renders_not_just_200(live_server):
    """
    This is the core blank-page regression test: it fails if the HTML loads
    but the React app never mounts (the exact bug this fix addresses).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.goto(live_server + "/")
        page.wait_for_selector(".panel", timeout=5000)  # raises if it never appears

        assert page.locator(".panel").count() >= 2, "Expected at least 2 panels (Profile, WOD Input) to render"
        assert page.locator("text=Athlete Profile").count() > 0
        assert page.locator("text=WOD Input").count() > 0
        assert page_errors == [], f"Uncaught JS errors on load: {page_errors}"
        browser.close()


@requires_playwright
def test_static_responses_are_not_heuristically_cacheable(live_server):
    """
    Regression test for the Edge-caching discrepancy: StaticFiles alone sends
    only Last-Modified/ETag, which lets browsers heuristically cache and
    silently serve a stale (possibly broken) page without hitting the
    network. The app must set an explicit Cache-Control on every response.
    """
    import httpx

    for path in ["/", "/vendor/react.development.js", "/vendor/babel.min.js"]:
        resp = httpx.get(live_server + path)
        assert resp.status_code == 200
        cache_control = resp.headers.get("cache-control", "")
        assert "no-cache" in cache_control, f"{path} is missing an explicit no-cache Cache-Control header: {cache_control!r}"


MOBILE_VIEWPORTS = [
    (375, 812, "iPhone X/11/12 mini"),
    (390, 844, "iPhone 12/13/14"),
    (393, 852, "iPhone 14/15 Pro"),
    (412, 915, "Android (Pixel/Galaxy)"),
]


@requires_playwright
@pytest.mark.parametrize("width,height,label", MOBILE_VIEWPORTS)
def test_mobile_viewport_no_overflow_and_touch_targets(live_server, width, height, label):
    """
    Real mobile regression test (not just a one-off manual check): verifies
    no horizontal overflow and that the primary button meets a 44px minimum
    touch-target height at each required smartphone viewport.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(live_server + "/")
        page.wait_for_selector(".panel")

        body_width = page.evaluate("document.body.scrollWidth")
        assert body_width <= width, f"{label} ({width}x{height}): horizontal overflow, body width {body_width}"

        save_button = page.locator("text=Save Profile")
        box = save_button.bounding_box()
        assert box["height"] >= 44, f"{label}: Save Profile button height {box['height']}px is below the 44px touch-target minimum"

        file_inputs = page.locator("input[type=file]")
        assert file_inputs.count() == 2, "Expected two file inputs (Take Photo + Choose from Gallery)"

        assert errors == [], f"{label}: uncaught JS errors: {errors}"
        browser.close()


@requires_playwright
def test_frontend_profile_creation_workflow(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_server + "/")
        page.wait_for_selector(".panel")

        inputs = page.locator("main input")
        inputs.nth(0).fill("Playwright Test Athlete")  # name field
        inputs.nth(1).fill("general fitness")  # goals field (required, min_length=1)
        page.locator("main >> text=Save Profile").click()

        page.wait_for_selector("text=Profile #", timeout=5000)
        assert page.locator("text=Profile #").count() > 0


@requires_playwright
def test_frontend_wod_textarea_and_button_render(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_server + "/")
        page.wait_for_selector(".panel")

        assert page.locator("textarea").count() == 1
        button = page.locator("text=Generate Coaching Plan")
        assert button.count() == 1
        assert button.is_disabled()  # disabled until a profile exists, per the UI logic
