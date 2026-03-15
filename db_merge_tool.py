#!/usr/bin/env python
"""Merge two SQLite gig databases, producing a superset with no duplicates.

Usage:
    python db_merge_tool.py --target test.db --source test.db.backup.sturok20260315 --dry-run
    python db_merge_tool.py --target test.db --source test.db.backup.sturok20260315 --commit

The target DB is treated as authoritative -- when records overlap (case-insensitive),
the target's version is kept. Records unique to the source are imported into the target.
"""

import argparse
import sqlite3
import sys


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_venues(conn):
    return conn.execute('SELECT * FROM venue').fetchall()


def get_all_gigs(conn):
    return conn.execute('SELECT * FROM gig').fetchall()


def venue_key(row):
    return row['venue'].strip().lower()


def gig_key(row):
    return (
        row['gig_date'],
        row['venue'].strip().lower(),
        row['band'].strip().lower(),
    )


def merge(target_path, source_path, commit):
    target = connect(target_path)
    source = connect(source_path)

    # --- Venues ---
    target_venues = get_all_venues(target)
    source_venues = get_all_venues(source)

    target_venue_keys = {venue_key(v) for v in target_venues}
    venues_to_add = [v for v in source_venues if venue_key(v) not in target_venue_keys]

    print('=== VENUE MERGE ===')
    print('Target venues: {}'.format(len(target_venues)))
    print('Source venues: {}'.format(len(source_venues)))
    print('Overlapping (kept from target): {}'.format(
        len([v for v in source_venues if venue_key(v) in target_venue_keys])))
    print('New venues to import from source: {}'.format(len(venues_to_add)))
    if venues_to_add:
        print()
        for v in sorted(venues_to_add, key=venue_key):
            cw = v['rt_miles_from_commonwealth']
            db = v['rt_miles_from_dry_bridge']
            cw_str = '{:.1f}'.format(cw) if cw else '-'
            db_str = '{:.1f}'.format(db) if db else '-'
            print('  + {} (city: {}, commonwealth: {}, dry_bridge: {})'.format(
                v['venue'], v['city'], cw_str, db_str))

    # --- Gigs ---
    target_gigs = get_all_gigs(target)
    source_gigs = get_all_gigs(source)

    target_gig_keys = {gig_key(g) for g in target_gigs}
    gigs_to_add = [g for g in source_gigs if gig_key(g) not in target_gig_keys]

    print()
    print('=== GIG MERGE ===')
    print('Target gigs: {}'.format(len(target_gigs)))
    print('Source gigs: {}'.format(len(source_gigs)))
    print('Overlapping (kept from target): {}'.format(
        len([g for g in source_gigs if gig_key(g) in target_gig_keys])))
    print('New gigs to import from source: {}'.format(len(gigs_to_add)))
    if gigs_to_add:
        print()
        years = sorted(set(g['gig_date'][:4] for g in gigs_to_add))
        for year in years:
            year_gigs = [g for g in gigs_to_add if g['gig_date'].startswith(year)]
            print('  {} ({} gigs):'.format(year, len(year_gigs)))
            for g in sorted(year_gigs, key=lambda x: x['gig_date']):
                print('    + {}  {}  {}  ${}'.format(
                    g['gig_date'], g['band'], g['venue'], g['pay']))

    # --- Summary ---
    print()
    total_venues_after = len(target_venues) + len(venues_to_add)
    total_gigs_after = len(target_gigs) + len(gigs_to_add)
    print('=== RESULT ===')
    print('After merge: {} venues, {} gigs'.format(total_venues_after, total_gigs_after))

    if not commit:
        print()
        print('DRY RUN -- no changes written. Re-run with --commit to apply.')
        target.close()
        source.close()
        return

    # --- Write ---
    print()
    print('Writing changes to {}...'.format(target_path))

    for v in venues_to_add:
        target.execute(
            'INSERT INTO venue (venue, rt_miles_from_commonwealth, rt_miles_from_dry_bridge, city) '
            'VALUES (?, ?, ?, ?)',
            (v['venue'], v['rt_miles_from_commonwealth'], v['rt_miles_from_dry_bridge'], v['city'])
        )

    for g in gigs_to_add:
        target.execute(
            'INSERT INTO gig (gig_date, venue, pay, band, trip_origin, comment) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (g['gig_date'], g['venue'], g['pay'], g['band'],
             g['trip_origin'], g['comment'])
        )

    target.commit()
    print('Done. Added {} venues and {} gigs.'.format(len(venues_to_add), len(gigs_to_add)))

    target.close()
    source.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge two gig SQLite databases.')
    parser.add_argument('--target', required=True, help='Target DB (authoritative, will be modified)')
    parser.add_argument('--source', required=True, help='Source DB to merge from')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    group.add_argument('--commit', action='store_true', help='Apply the merge')
    args = parser.parse_args()

    merge(args.target, args.source, args.commit)
