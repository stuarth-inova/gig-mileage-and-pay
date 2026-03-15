"""Form submission workflow tests."""

from app import db, Gig, Venue


VALID_GIG = {
    'date': '2014-06-15',
    'venue': "miller's",
    'band': 'Overdog',
    'pay': '85',
    'trip_origin': '2517 commonwealth',
    'comment': 'Test gig',
}


# --- Gig submission ---

def test_submit_gig_valid(client, seed_data):
    resp = client.post('/gigs/new_gig_data', data=VALID_GIG)
    assert resp.status_code == 200
    assert b'Overdog' in resp.data or b'Submit' in resp.data


def test_submit_gig_missing_pay(client, seed_data):
    data = {**VALID_GIG, 'pay': ''}
    resp = client.post('/gigs/new_gig_data', data=data)
    assert resp.status_code == 302
    assert 'submit' in resp.location


def test_submit_gig_missing_band(client, seed_data):
    data = {**VALID_GIG, 'band': ''}
    resp = client.post('/gigs/new_gig_data', data=data)
    assert resp.status_code == 302
    assert 'submit' in resp.location


def test_submit_gig_missing_date(client, seed_data):
    data = {**VALID_GIG, 'date': ''}
    resp = client.post('/gigs/new_gig_data', data=data)
    assert resp.status_code == 302
    assert 'submit' in resp.location


def test_submit_gig_duplicate(client, seed_data):
    data = {
        'date': '2014-01-18',
        'venue': "miller's",
        'band': 'The Cows',
        'pay': '71',
        'trip_origin': '2517 commonwealth',
        'comment': '',
    }
    resp = client.post('/gigs/new_gig_data', data=data)
    assert resp.status_code == 302
    assert 'submit' in resp.location


def test_submit_gig_unknown_venue(client, seed_data):
    data = {**VALID_GIG, 'venue': 'nonexistent place'}
    resp = client.post('/gigs/new_gig_data', data=data)
    assert resp.status_code == 302
    assert 'add_venue' in resp.location


def test_submit_gig_get_rejected(client, seed_data):
    resp = client.get('/gigs/new_gig_data')
    assert resp.status_code == 200
    assert b'Improper' in resp.data or b'error' in resp.data.lower()


# --- Venue submission ---

def test_add_venue_valid(client, app):
    data = {
        'venue': 'New Test Venue',
        'rt_miles_from_commonwealth': '42.5',
        'rt_miles_from_dry_bridge': '30.0',
        'city': 'testville',
    }
    resp = client.post('/venue/add_venue', data=data)
    assert resp.status_code == 200
    with app.app_context():
        v = Venue.query.filter_by(venue='new test venue').first()
        assert v is not None
        assert v.rt_miles_from_commonwealth == 42.5
        assert v.rt_miles_from_dry_bridge == 30.0


def test_add_venue_empty_commonwealth(client, app):
    data = {
        'venue': 'Dry Bridge Only Venue',
        'rt_miles_from_commonwealth': '',
        'rt_miles_from_dry_bridge': '25.0',
        'city': 'somewhere',
    }
    resp = client.post('/venue/add_venue', data=data)
    assert resp.status_code == 200
    with app.app_context():
        v = Venue.query.filter_by(venue='dry bridge only venue').first()
        assert v is not None
        assert v.rt_miles_from_commonwealth is None
        assert v.rt_miles_from_dry_bridge == 25.0


def test_add_venue_empty_dry_bridge(client, app):
    data = {
        'venue': 'Commonwealth Only Venue',
        'rt_miles_from_commonwealth': '15.0',
        'rt_miles_from_dry_bridge': '',
        'city': 'elsewhere',
    }
    resp = client.post('/venue/add_venue', data=data)
    assert resp.status_code == 200
    with app.app_context():
        v = Venue.query.filter_by(venue='commonwealth only venue').first()
        assert v is not None
        assert v.rt_miles_from_commonwealth == 15.0
        assert v.rt_miles_from_dry_bridge is None


def test_add_venue_get_renders_form(client):
    resp = client.get('/venue/add_venue')
    assert resp.status_code == 200
    assert b'Venue' in resp.data
