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
def test_vendor_scripts_load_from_real_local_files_without_false_positive(live_server):
    """
    Regression test for a real production bug (2026-10-26): the previous
    vendor-script watchdog fired a one-shot check at exactly 3 seconds and
    declared failure if React/ReactDOM/Babel weren't yet defined — a false
    positive on any connection slower than fast broadband, since the combined
    vendor payload is ~3.5MB. This test uses the REAL local vendor/*.js files
    served by the REAL live server (no mocked React/ReactDOM/Babel, no CDN
    fetch) and waits past the old 3-second window to confirm no false
    failure message appears once the app has actually mounted.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_server + "/")
        page.wait_for_selector(".panel", timeout=20000)
        page.wait_for_timeout(3500)  # past the old (buggy) 3-second one-shot check

        boot_status = page.locator("#boot-status")
        # #boot-status is removed once React mounts into #root, replacing its contents.
        assert boot_status.count() == 0, "boot-status placeholder/error should be gone once the app has mounted"
        assert page.locator("text=failed to load").count() == 0, "No false-positive load-failure message should appear"
        browser.close()


@requires_playwright
def test_vendor_script_failure_reports_exact_failing_file(live_server):
    """
    Regression test for the fix's diagnostic improvement: when a vendor
    script genuinely fails to load (simulated here by aborting the real
    network request to babel.min.js — the actual file, not a mock), the
    error message must name the exact failing file, not a generic
    "one or more scripts" message.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.route("**/vendor/babel.min.js", lambda route: route.abort())
        page.goto(live_server + "/")
        page.wait_for_timeout(16000)  # past the new 15-second grace window

        boot_text = page.locator("#boot-status").inner_text()
        assert "babel.min.js" in boot_text, f"Error message should name the exact failing file, got: {boot_text}"
        assert "Babel" in boot_text
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
def test_cost_display_shows_unavailable_for_unverified_pricing(live_server, monkeypatch):
    """
    Regression test for the misleading '$0.000000' display found via a real
    saved coaching-plan PDF (see AI_prompts.md). Pricing is a documented
    UNVERIFIED placeholder (PRICING_PER_MILLION_TOKENS_UNVERIFIED = 0), so
    estimated_cost_usd is always 0 today — the UI must say so explicitly
    rather than showing a bare "$0.000000" that reads as "this was free."
    """
    from app import agent as agent_module

    def _fake_call_model(system_prompt, user_prompt, json_mode=True):
        if "WOD parser" in system_prompt:
            content = '{"format": "AMRAP", "time_cap_minutes": 12, "exercises": [{"name": "Air Squats", "scheme": "AMRAP", "reps": "10", "load_note": null}], "notes": null}'
        else:
            content = (
                '{"warm_up": ["easy rowing"], "scaling_options": ["reduce reps"], '
                '"main_workout_guidance": "pace yourself", "complementary_exercises": ["Back squat"], '
                '"safety_notes": ["stop on sharp pain"]}'
            )
        return {"content": content, "prompt_tokens": 100, "completion_tokens": 50, "cached_tokens": 0,
                "estimated_cost_usd": 0.0, "latency_ms": 5, "model": "gpt-6-luna"}

    monkeypatch.setattr(agent_module, "call_model", _fake_call_model)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_server + "/")
        page.wait_for_selector(".panel")

        inputs = page.locator("main input")
        inputs.nth(0).fill("Cost Display Test")
        inputs.nth(1).fill("general fitness")
        page.locator("main >> text=Save Profile").click()
        page.wait_for_selector("text=Profile #")

        page.locator("textarea").fill("AMRAP 12 minutes 10 Air Squats")
        page.locator("text=Generate Coaching Plan").click()
        page.wait_for_selector("text=Personalized Coaching Plan", timeout=10000)

        cost_value = page.locator(".usage-cost .usage-value").inner_text()
        assert "unavailable" in cost_value.lower() and "pricing unverified" in cost_value.lower(), \
            f"Expected the honest unverified-pricing message, got: {cost_value!r}"
        assert page.locator("text=$0.000000").count() == 0, "A misleading $0.000000 figure must never be shown"
        browser.close()


@requires_playwright
def test_stale_scan_warning_clears_on_manual_edit(live_server, monkeypatch):
    """
    Regression test for a real bug found via a saved coaching-plan PDF: a
    low-confidence scan warning stayed visible even after the user fully
    retyped the WOD text, misattributing an old scan's uncertainty to
    manually-reviewed content (see AI_prompts.md). A fresh scan must still
    show its own warning immediately (not cleared prematurely) until the
    user edits the text themselves.
    """
    from app import agent as agent_module

    def _fake_call_model_with_image(system, user_text, image_base64, mime_type="image/png"):
        return {"content": "[unclear: illegible]", "prompt_tokens": 50, "completion_tokens": 20, "cached_tokens": 0,
                "estimated_cost_usd": 0.0, "latency_ms": 5, "model": "gpt-6-luna"}

    monkeypatch.setattr(agent_module, "call_model_with_image", _fake_call_model_with_image)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_server + "/")
        page.wait_for_selector(".panel")

        gallery_input = page.locator("input[type=file]").nth(1)
        gallery_input.set_input_files(
            {"name": "test.png", "mimeType": "image/png", "buffer": b"\x89PNG\r\n\x1a\nfake"}
        )
        page.wait_for_timeout(1000)

        # Warning must still be visible right after scanning — never cleared prematurely.
        assert page.locator("text=may be unclear").count() > 0, "Low-confidence warning should appear right after a low-confidence scan"

        # Manually editing the textarea must clear the stale warning.
        page.locator("textarea").fill("AMRAP 12 minutes 10 Air Squats 8 Push-ups 6 Burpees")
        page.wait_for_timeout(200)
        assert page.locator("text=may be unclear").count() == 0, "Stale scan warning must clear once the user manually edits the text"
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


def _mock_agent_for_trace_ui(monkeypatch):
    """Shared mock producing a real-shaped coaching response, no paid calls."""
    from app import agent as agent_module

    def _fake_call_model(system_prompt, user_prompt, json_mode=True):
        if "WOD parser" in system_prompt:
            content = '{"format": "AMRAP", "time_cap_minutes": 12, "exercises": [{"name": "Air Squats", "scheme": "AMRAP", "reps": "10", "load_note": null}], "notes": null}'
        else:
            content = (
                '{"warm_up": ["easy rowing"], "scaling_options": ["reduce reps"], '
                '"main_workout_guidance": "pace yourself", "complementary_exercises": ["Back squat"], '
                '"safety_notes": ["stop on sharp pain"]}'
            )
        return {"content": content, "prompt_tokens": 393, "completion_tokens": 982, "cached_tokens": 0,
                "estimated_cost_usd": 0.0, "latency_ms": 5, "model": "gpt-6-luna"}

    monkeypatch.setattr(agent_module, "call_model", _fake_call_model)


@requires_playwright
def test_agent_trace_cards_collapsed_by_default_and_expand_on_click(live_server, monkeypatch):
    """
    Regression test for the Agent Trace redesign: each tool call renders as
    a distinct card showing tool name/duration/status by default, with
    input/output hidden until "View details" is clicked — and the real
    trace data (tool order, timings, content) must still be present once
    expanded, never summarized away.
    """
    _mock_agent_for_trace_ui(monkeypatch)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_server + "/")
        page.wait_for_selector(".panel")

        inputs = page.locator("main input")
        inputs.nth(0).fill("Trace UI Test")
        inputs.nth(1).fill("general fitness")
        page.locator("main >> text=Save Profile").click()
        page.wait_for_selector("text=Profile #")

        page.locator("textarea").fill("AMRAP 12 minutes 10 Air Squats")
        page.locator("text=Generate Coaching Plan").click()
        page.wait_for_selector("text=Personalized Coaching Plan", timeout=10000)

        cards = page.locator(".trace-card")
        assert cards.count() == 4, "Expected 4 tool-call cards (parse, validate, generate, validate)"

        # Collapsed by default: no input/output text visible yet.
        assert page.locator(".trace-details").count() == 0, "Details should be collapsed by default"
        assert page.locator("text=View details").count() == 4

        # Expand the first card and confirm real data appears.
        cards.nth(0).locator(".trace-card-header").click()
        page.wait_for_timeout(100)
        assert page.locator(".trace-details").count() == 1
        assert page.locator("text=Hide details").count() == 1
        details_text = page.locator(".trace-details").first.inner_text()
        assert "AMRAP" in details_text or "Air Squats" in details_text, "Real input/output content must be visible when expanded"
        browser.close()


@requires_playwright
def test_agent_trace_and_usage_no_horizontal_overflow_at_mobile_widths(live_server, monkeypatch):
    """
    Regression test: long JSON output in an expanded trace card must wrap,
    never cause horizontal scrolling, at every required mobile viewport.
    """
    _mock_agent_for_trace_ui(monkeypatch)
    for width, height in [(375, 812), (390, 844), (412, 915)]:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(live_server + "/")
            page.wait_for_selector(".panel")

            inputs = page.locator("main input")
            inputs.nth(0).fill("Overflow Test")
            inputs.nth(1).fill("general fitness")
            page.locator("main >> text=Save Profile").click()
            page.wait_for_selector("text=Profile #")

            page.locator("textarea").fill("AMRAP 12 minutes 10 Air Squats")
            page.locator("text=Generate Coaching Plan").click()
            page.wait_for_selector("text=Personalized Coaching Plan", timeout=10000)

            # Expand every trace card to exercise the longest real JSON output.
            for i in range(page.locator(".trace-card").count()):
                page.locator(".trace-card-header").nth(i).click()
            page.wait_for_timeout(200)

            body_width = page.evaluate("document.body.scrollWidth")
            assert body_width <= width, f"{width}x{height}: horizontal overflow (body width {body_width}) with all trace cards expanded"

            usage_grid = page.locator(".usage-grid")
            assert usage_grid.count() == 1
            browser.close()
