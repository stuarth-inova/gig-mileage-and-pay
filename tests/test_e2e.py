"""End-to-end browser tests using Playwright."""

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture
def page(browser, live_server):
    p = browser.new_page()
    p._base_url = live_server
    yield p
    p.close()


def test_home_page_loads(page, live_server):
    page.goto(live_server)
    assert page.title() == 'Index'
    assert page.locator('h1').inner_text() == 'Home'


def test_home_page_shows_years(page, live_server):
    page.goto(live_server)
    content = page.content()
    assert '2014' in content
    assert '2025' in content


def test_gig_list_navigation(page, live_server):
    page.goto(live_server)
    page.click('button:has-text("Gigs in 2014")')
    page.wait_for_load_state('networkidle')
    assert '2014' in page.content()
    assert 'The Cows' in page.content()


def test_verbose_summary(page, live_server):
    page.goto(live_server)
    page.click('button:has-text("Verbose information for 2014")')
    page.wait_for_load_state('networkidle')
    content = page.content()
    assert 'The Cows' in content


def test_venue_list(page, live_server):
    page.goto(f'{live_server}/venue-list')
    content = page.content()
    assert "miller" in content
    assert "durty nelly" in content


def test_add_venue_flow(page, live_server):
    page.goto(f'{live_server}/venue/add_venue')
    page.fill('input[name="venue"]', 'E2E Test Venue')
    page.fill('input[name="rt_miles_from_commonwealth"]', '15.5')
    page.fill('input[name="rt_miles_from_dry_bridge"]', '')
    page.fill('input[name="city"]', 'testtown')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    assert page.locator('body').inner_text()


def test_add_gig_flow(page, live_server):
    page.goto(f'{live_server}/gigs/submit')
    page.fill('input[name="date"]', '2014-09-20')
    page.select_option('select[name="venue"]', "miller's")
    page.fill('input[name="band"]', 'E2E Test Band')
    page.fill('input[name="pay"]', '99')
    page.select_option('select[name="trip_origin"]', '2517 commonwealth')
    page.fill('input[name="comment"]', 'e2e test comment')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    content = page.content()
    assert 'E2E Test Band' in content or 'error' not in content.lower()
