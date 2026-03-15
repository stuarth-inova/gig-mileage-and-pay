"""Mileage, pay, and summary calculation tests.

Seed data reference (from conftest.py):
    2014 gigs (all 2517 commonwealth):
        miller's       $71   rt_commonwealth=9.2
        durty nelly's  $52   rt_commonwealth=9.0
        pro re nata    $425  rt_commonwealth=28.8
        => total pay=$548, total miles=47.0, 3 gigs

    2025 gigs (all 741 dry bridge):
        durty nelly's  $100  rt_dry_bridge=24.0
        pro re nata    $102  rt_dry_bridge=12.6
        => total pay=$202, total miles=36.6, 2 gigs
"""

from app import (
    unique_year_list,
    annual_gig_pay_miles_summary,
    simple_sum_gig_mileage,
    calculate_annual_by_band,
    accumulate_gig_mileage_by_venue,
    db_printable_gig_list,
)


def test_unique_year_list(app, seed_data):
    with app.app_context():
        years = unique_year_list()
        assert years == [2014, 2025]


def test_unique_year_list_empty_db(app):
    with app.app_context():
        years = unique_year_list()
        assert years == []


def test_annual_summary_2014(app, seed_data):
    with app.app_context():
        miles, pay, n_gigs, year, unmatched = annual_gig_pay_miles_summary(2014, False)
        assert n_gigs == 3
        assert pay == 548.0
        assert abs(miles - 47.0) < 0.01
        assert unmatched == []


def test_annual_summary_2025(app, seed_data):
    with app.app_context():
        miles, pay, n_gigs, year, unmatched = annual_gig_pay_miles_summary(2025, False)
        assert n_gigs == 2
        assert pay == 202.0
        assert abs(miles - 36.6) < 0.01


def test_annual_summary_verbose_no_unmatched(app, seed_data):
    with app.app_context():
        _, _, _, _, unmatched = annual_gig_pay_miles_summary(2014, True)
        assert unmatched == []


def test_annual_summary_verbose_with_unmatched(app, seed_data):
    """Add a gig at a venue with no matching distance for its trip origin."""
    from app import db, Gig
    from datetime import date
    with app.app_context():
        db.session.add(Gig(
            gig_date=date(2014, 8, 1), venue="the mystery",
            pay=50.0, band='Test Band', trip_origin='2517 commonwealth',
        ))
        db.session.commit()
        _, _, _, _, unmatched = annual_gig_pay_miles_summary(2014, True)
        assert 'the mystery' in unmatched


def test_annual_summary_empty_year(app, seed_data):
    with app.app_context():
        miles, pay, n_gigs, year, unmatched = annual_gig_pay_miles_summary(1999, False)
        assert n_gigs == 0
        assert pay == 0.0
        assert miles == 0.0


def test_simple_sum_mileage_commonwealth(app, seed_data):
    with app.app_context():
        input_list = [
            ('2517 commonwealth', "miller's"),
            ('2517 commonwealth', "durty nelly's"),
        ]
        total = simple_sum_gig_mileage(input_list)
        assert abs(total - 18.2) < 0.01  # 9.2 + 9.0


def test_simple_sum_mileage_dry_bridge(app, seed_data):
    with app.app_context():
        input_list = [
            ('741 dry bridge', "durty nelly's"),
            ('741 dry bridge', "pro re nata"),
        ]
        total = simple_sum_gig_mileage(input_list)
        assert abs(total - 36.6) < 0.01  # 24.0 + 12.6


def test_simple_sum_mileage_missing_venue(app, seed_data):
    with app.app_context():
        input_list = [
            ('2517 commonwealth', "miller's"),
            ('2517 commonwealth', 'no such venue'),
        ]
        total = simple_sum_gig_mileage(input_list)
        assert abs(total - 9.2) < 0.01


def test_calculate_annual_by_band_2014(app, seed_data):
    with app.app_context():
        stats = calculate_annual_by_band(2014)
        band_dict = {band: (pay, miles) for band, pay, miles in stats}
        assert 'Alligator' in band_dict
        assert band_dict['Alligator'][0] == 425.0
        assert abs(band_dict['Alligator'][1] - 28.8) < 0.01
        assert 'The Cows' in band_dict
        assert band_dict['The Cows'][0] == 71.0


def test_accumulate_mileage_by_venue(app, seed_data):
    with app.app_context():
        gig_list = [
            ('2517 commonwealth', "miller's"),
            ('2517 commonwealth', "miller's"),
            ('2517 commonwealth', 'no such venue'),
        ]
        result = accumulate_gig_mileage_by_venue(gig_list)
        assert abs(result["miller's"] - 18.4) < 0.01  # 9.2 * 2
        assert result['no such venue'] == 'Not matched for mileage'


def test_db_printable_gig_list_2014(app, seed_data):
    with app.app_context():
        gigs = db_printable_gig_list(2014).all()
        assert len(gigs) == 3
        assert gigs[0].gig_date.year == 2014


def test_db_printable_gig_list_empty_year(app, seed_data):
    with app.app_context():
        gigs = db_printable_gig_list(1999).all()
        assert len(gigs) == 0
