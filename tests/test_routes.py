"""Route response tests -- status codes and key content."""


def test_index_empty_db(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Home' in resp.data


def test_index_with_data(client, seed_data):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'2014' in resp.data
    assert b'2025' in resp.data


def test_home_alias(client):
    resp = client.get('/home')
    assert resp.status_code == 200


def test_index_alias(client):
    resp = client.get('/index')
    assert resp.status_code == 200


def test_gigs_redirects_to_index(client):
    resp = client.get('/gigs')
    assert resp.status_code == 302
    assert resp.location == '/'


def test_gigs_slash_redirects(client):
    resp = client.get('/gigs/')
    assert resp.status_code == 302


def test_gig_redirects(client):
    resp = client.get('/gig')
    assert resp.status_code == 302


def test_gig_details_with_data(client, seed_data):
    resp = client.get('/gigs/2014')
    assert resp.status_code == 200
    assert b'The Cows' in resp.data
    assert b"miller" in resp.data


def test_gig_details_empty_year(client, seed_data):
    resp = client.get('/gigs/1999')
    assert resp.status_code == 200


def test_venue_list(client, seed_data):
    resp = client.get('/venue-list')
    assert resp.status_code == 200
    assert b"miller" in resp.data
    assert b"durty nelly" in resp.data


def test_summary_no_year(client):
    resp = client.get('/summary')
    assert resp.status_code == 200
    assert b'Please include year' in resp.data


def test_summary_with_year(client, seed_data):
    resp = client.get('/summary/2014')
    assert resp.status_code == 200
    assert b'548' in resp.data  # $548.00 total pay (71+52+425)


def test_summary_verbose(client, seed_data):
    resp = client.get('/summary/2014/verbose')
    assert resp.status_code == 200
    assert b'The Cows' in resp.data
    assert b'Alligator' in resp.data


def test_hello_no_name(client):
    resp = client.get('/hello')
    assert resp.status_code == 200


def test_hello_with_name(client):
    resp = client.get('/hello/World')
    assert resp.status_code == 200
    assert b'World' in resp.data


def test_gig_submit_form(client, seed_data):
    resp = client.get('/gigs/submit')
    assert resp.status_code == 200
    assert b'Submit' in resp.data


def test_venue_add_form(client):
    resp = client.get('/venue/add_venue')
    assert resp.status_code == 200
    assert b'Venue' in resp.data
