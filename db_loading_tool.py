#!/usr/bin/env python

import argparse
import csv
import os
from datetime import date, datetime

from app import db, Gig, Venue
from calc_miles_and_pay import process_distances_input_csv

BASEDIR = os.path.abspath(os.path.dirname(__file__))

QUOTE_REPLACEMENTS = {
    '\u2019': "'",  # right single quotation mark
    '\u2018': "'",  # left single quotation mark
    '\u201c': '"',  # left double quotation mark
    '\u201d': '"',  # right double quotation mark
}


def normalize_quotes(text):
    for fancy, plain in QUOTE_REPLACEMENTS.items():
        text = text.replace(fancy, plain)
    return text


db.create_all()


def gig_exists(gig_date, venue, band):
    return Gig.query.filter_by(gig_date=gig_date, venue=venue, band=band).first() is not None


def venue_exists(venue_name):
    return Venue.query.filter_by(venue=venue_name).first() is not None


def populate_venue_distance_data(venue_dict):
    added = 0
    skipped = 0
    for venue in venue_dict:
        if venue_exists(venue):
            skipped += 1
            continue

        try:
            rt_commonwealth = float(venue_dict[venue]['round_trip_commonwealth'])
        except (ValueError, TypeError):
            rt_commonwealth = None

        try:
            rt_dry_bridge = float(venue_dict[venue]['round_trip_dry_br'])
        except (ValueError, TypeError):
            rt_dry_bridge = None

        new_venue = Venue(venue=venue, rt_miles_from_commonwealth=rt_commonwealth,
                          rt_miles_from_dry_bridge=rt_dry_bridge,
                          city=venue_dict[venue]['city'])
        db.session.add(new_venue)
        db.session.commit()
        added += 1

    print('Venues: {} added, {} skipped (already exist)'.format(added, skipped))


def populate_gig_data_from_giglog(csv_path, year):
    """Import gigs from GigLog_excel CSV files that have placeholder dates (MM/DD/YY).

    Expected columns: Band, Venue, Date, Pay, R/T Miles
    Uses day=1 for all dates since original day data is lost.
    Sets trip_origin to '2517 commonwealth' (all pre-move gigs).
    """
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        added = 0
        skipped = 0
        for row in reader:
            band = row.get('Band', '').strip()
            if not band:
                continue

            venue = normalize_quotes(row.get('Venue', '')).strip().lower()
            pay_str = row.get('Pay', '0').strip().lstrip('$').replace(',', '')
            try:
                pay = float(pay_str) if pay_str else 0.0
            except ValueError:
                pay = 0.0

            date_str = row.get('Date', '').strip()
            try:
                month = int(date_str.split('/')[0])
            except (ValueError, IndexError):
                continue
            gig_date = date(year, month, 1)

            if gig_exists(gig_date, venue, band):
                skipped += 1
                continue

            new_gig = Gig(
                gig_date=gig_date,
                band=band,
                venue=venue,
                pay=pay,
                trip_origin='2517 commonwealth',
                comment=None,
            )
            db.session.add(new_gig)
            db.session.commit()
            added += 1
        print('{}: {} gigs added, {} skipped (duplicates)'.format(csv_path, added, skipped))


def populate_gig_data_2025(csv_path):
    """Import gigs from the 2025-format CSV with real dates and trip_origin.

    Expected columns: Band, Venue, Date, Pay, R/T miles, trip_origin, comment
    First row of file is a title row (not headers) -- headers are on the second row.
    Date format: "Mon DD, YYYY" (e.g. "Jan 23, 2025")
    """
    with open(csv_path, 'r') as f:
        next(f)  # skip title row ("gigs_2025")
        reader = csv.DictReader(f)
        added = 0
        skipped = 0
        for row in reader:
            band = row.get('Band', '').strip()
            if not band:
                continue

            venue = normalize_quotes(row.get('Venue', '')).strip().lower()
            pay_str = row.get('Pay', '0').strip().lstrip('$').replace(',', '')
            try:
                pay = float(pay_str) if pay_str else 0.0
            except ValueError:
                pay = 0.0

            date_str = row.get('Date', '').strip()
            try:
                gig_date = datetime.strptime(date_str, '%b %d, %Y').date()
            except ValueError:
                print('  Skipping row with unparseable date: "{}"'.format(date_str))
                continue

            trip_origin = row.get('trip_origin', '').strip().lower()
            if not trip_origin:
                trip_origin = '741 dry bridge'

            comment = normalize_quotes(row.get('comment', '')).strip() or None

            if gig_exists(gig_date, venue, band):
                skipped += 1
                continue

            new_gig = Gig(
                gig_date=gig_date,
                band=band,
                venue=venue,
                pay=pay,
                trip_origin=trip_origin,
                comment=comment,
            )
            db.session.add(new_gig)
            db.session.commit()
            added += 1
        print('{}: {} gigs added, {} skipped (duplicates)'.format(csv_path, added, skipped))


def populate_gig_data_2014(csv_path):
    """Import gigs from the 2014-format CSV with real MM/DD/YY dates.

    Expected columns: Band, Venue, Date, Pay, R_T_Miles, [comment]
    The trailing comma in the header creates an empty 6th column which
    occasionally contains a comment.
    """
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        added = 0
        skipped = 0
        for row in reader:
            if len(row) < 5:
                continue
            band = normalize_quotes(row[0]).strip()
            if not band:
                continue

            venue = normalize_quotes(row[1]).strip().lower()

            date_str = row[2].strip()
            try:
                gig_date = datetime.strptime(date_str, '%m/%d/%y').date()
            except ValueError:
                print('  Skipping row with unparseable date: "{}"'.format(date_str))
                continue

            pay_str = row[3].strip().lstrip('$').replace(',', '')
            try:
                pay = float(pay_str) if pay_str else 0.0
            except ValueError:
                pay = 0.0

            comment = None
            if len(row) > 5 and row[5].strip():
                comment = normalize_quotes(row[5]).strip()

            if gig_exists(gig_date, venue, band):
                skipped += 1
                continue

            new_gig = Gig(
                gig_date=gig_date,
                band=band,
                venue=venue,
                pay=pay,
                trip_origin='2517 commonwealth',
                comment=comment,
            )
            db.session.add(new_gig)
            db.session.commit()
            added += 1
        print('{}: {} gigs added, {} skipped (duplicates)'.format(csv_path, added, skipped))


def load_all_data():
    """Load all venue and gig data from CSV sources."""

    # Venue/distance data
    distances_csv = os.path.join(BASEDIR, 'gig-mileage-data-distances.csv')
    print('Loading venue distances from {}'.format(distances_csv))
    distances = process_distances_input_csv(distances_csv)
    populate_venue_distance_data(distances.return_venue_dictionary())

    # 2012 gig data (placeholder dates)
    gig_2012_csv = os.path.join(BASEDIR, 'GigLog_excel', '2012-Table 1.csv')
    print('Loading 2012 gig data...')
    populate_gig_data_from_giglog(gig_2012_csv, 2012)

    # 2014 gig data (real MM/DD/YY dates)
    gig_2014_csv = os.path.join(BASEDIR, 'GigLog_excel', 'gigs_2014.csv')
    print('Loading 2014 gig data...')
    populate_gig_data_2014(gig_2014_csv)

    # 2025 gig data (real dates)
    gig_2025_csv = os.path.join(BASEDIR, 'GigLog_excel', 'gigs_2025.csv')
    print('Loading 2025 gig data...')
    populate_gig_data_2025(gig_2025_csv)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load gig and venue data into the database.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--fresh', action='store_true',
                       help='Delete existing database and reimport everything from scratch')
    group.add_argument('--append', action='store_true',
                       help='Add new data only, skip duplicates')
    args = parser.parse_args()

    if not args.fresh and not args.append:
        print('Usage: python db_loading_tool.py [--fresh | --append]')
        print('  --fresh   Delete test.db and reimport all data from scratch')
        print('  --append  Import data, skipping any duplicates')
        raise SystemExit(1)

    if args.fresh:
        db_path = os.path.join(BASEDIR, 'test.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print('Deleted existing database: {}'.format(db_path))
        db.create_all()
        print('Created fresh database schema')

    load_all_data()
    print('\nDone.')
