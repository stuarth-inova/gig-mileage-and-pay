import os
import sys
import threading
import pytest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app, db, Gig, Venue

ORIGINAL_DB_URI = flask_app.config['SQLALCHEMY_DATABASE_URI']


def _switch_to_test_db():
    """Point SQLAlchemy at an in-memory database and dispose the old engine."""
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['TESTING'] = True
    if db.engine:
        db.engine.dispose()


def _restore_production_db():
    """Restore the original database URI so flask run is unaffected."""
    db.session.remove()
    if db.engine:
        db.engine.dispose()
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = ORIGINAL_DB_URI
    flask_app.config['TESTING'] = False


@pytest.fixture
def app():
    _switch_to_test_db()

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    _restore_production_db()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_data(app):
    """Populate the in-memory DB with a small, deterministic dataset.

    Venues:
        miller's       - commonwealth: 9.2,  dry_bridge: 23.0
        durty nelly's  - commonwealth: 9.0,  dry_bridge: 24.0
        pro re nata    - commonwealth: 28.8, dry_bridge: 12.6
        the mystery    - commonwealth: None, dry_bridge: 50.0  (missing one distance)

    Gigs (2014): 3 gigs, 2 bands, all commonwealth origin
        2014-01-18  The Cows     miller's       $71
        2014-03-07  Unl. Dev.    durty nelly's  $52
        2014-05-17  Alligator    pro re nata    $425

    Gigs (2025): 2 gigs, dry bridge origin
        2025-01-23  Nightfall    durty nelly's  $100
        2025-07-25  Mama Tried   pro re nata    $102
    """
    with app.app_context():
        venues = [
            Venue(venue="miller's", rt_miles_from_commonwealth=9.2,
                  rt_miles_from_dry_bridge=23.0, city='cville'),
            Venue(venue="durty nelly's", rt_miles_from_commonwealth=9.0,
                  rt_miles_from_dry_bridge=24.0, city='cville'),
            Venue(venue="pro re nata", rt_miles_from_commonwealth=28.8,
                  rt_miles_from_dry_bridge=12.6, city='crozet'),
            Venue(venue="the mystery", rt_miles_from_commonwealth=None,
                  rt_miles_from_dry_bridge=50.0, city='nowhere'),
        ]
        for v in venues:
            db.session.add(v)

        gigs = [
            Gig(gig_date=date(2014, 1, 18), venue="miller's", pay=71.0,
                band='The Cows', trip_origin='2517 commonwealth'),
            Gig(gig_date=date(2014, 3, 7), venue="durty nelly's", pay=52.0,
                band='Unlimited Devotion', trip_origin='2517 commonwealth'),
            Gig(gig_date=date(2014, 5, 17), venue="pro re nata", pay=425.0,
                band='Alligator', trip_origin='2517 commonwealth'),
            Gig(gig_date=date(2025, 1, 23), venue="durty nelly's", pay=100.0,
                band='Nightfall of Diamonds', trip_origin='741 dry bridge'),
            Gig(gig_date=date(2025, 7, 25), venue="pro re nata", pay=102.0,
                band='Mama Tried', trip_origin='741 dry bridge'),
        ]
        for g in gigs:
            db.session.add(g)

        db.session.commit()


@pytest.fixture(scope='session')
def _live_server_url():
    """Start a real Flask server once for all Playwright tests."""
    port = 5199
    _switch_to_test_db()

    with flask_app.app_context():
        db.create_all()

        venues = [
            Venue(venue="miller's", rt_miles_from_commonwealth=9.2,
                  rt_miles_from_dry_bridge=23.0, city='cville'),
            Venue(venue="durty nelly's", rt_miles_from_commonwealth=9.0,
                  rt_miles_from_dry_bridge=24.0, city='cville'),
            Venue(venue="pro re nata", rt_miles_from_commonwealth=28.8,
                  rt_miles_from_dry_bridge=12.6, city='crozet'),
        ]
        for v in venues:
            db.session.add(v)

        gigs = [
            Gig(gig_date=date(2014, 1, 18), venue="miller's", pay=71.0,
                band='The Cows', trip_origin='2517 commonwealth'),
            Gig(gig_date=date(2014, 3, 7), venue="durty nelly's", pay=52.0,
                band='Unlimited Devotion', trip_origin='2517 commonwealth'),
            Gig(gig_date=date(2025, 1, 23), venue="durty nelly's", pay=100.0,
                band='Nightfall of Diamonds', trip_origin='741 dry bridge'),
        ]
        for g in gigs:
            db.session.add(g)
        db.session.commit()

    server = threading.Thread(
        target=lambda: flask_app.run(port=port, use_reloader=False),
        daemon=True,
    )
    server.start()
    import time
    time.sleep(0.5)
    yield f'http://127.0.0.1:{port}'

    _restore_production_db()


@pytest.fixture
def live_server(_live_server_url):
    return _live_server_url
