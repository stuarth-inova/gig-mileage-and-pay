#!/usr/bin/env python

from app import db
from app import Gig
from app import Venue
from sqlalchemy import asc
from calc_miles_and_pay import process_gig_input_csv
from calc_miles_and_pay import process_distances_input_csv
from datetime import date

db.create_all()


def populate_venue_distance_data(venue_dict):
    for venue in venue_dict:
        try:
            rt_commonwealth_corrected = float(venue_dict[venue]['round_trip_commonwealth'])
        except ValueError as ve:
            rt_commonwealth_corrected = None
        except TypeError as te:
            rt_commonwealth_corrected = None

        try:
            rt_dry_bridge_corrected = float(venue_dict[venue]['round_trip_dry_br'])
        except ValueError as ve:
            rt_dry_bridge_corrected = None
        except TypeError as te:
            rt_dry_bridge_corrected = None

        add_venue = Venue(venue=venue, rt_miles_from_commonwealth=rt_commonwealth_corrected,
                          rt_miles_from_dry_bridge=rt_dry_bridge_corrected,
                          city=venue_dict[venue]['city'])

        db.session.add(add_venue)
        db.session.commit()


def populate_trial_fake_gig_data():
    gig1 = Gig(gig_date=date(2019, 1, 17), venue='Millers', pay=50, band='Cows')
    gig2 = Gig(gig_date=date(2019, 1, 25), venue='Ix', pay=80.50, band='Mama Tried')

    db.session.add(gig1)
    db.session.add(gig2)
    db.session.commit()


def print_gigs_dictionary():
    for gig in gigs_dictionary:
        print('{} - type: {}'.format(gig, type(gig)))
        print('{}'.format(gigs_dictionary[gig]))


def populate_gig_data(gigs_dict):
    for gig in gigs_dict:
        try:
            add_gig = Gig(gig_date=gigs_dict[gig]['date'], band=gigs_dict[gig]['band'], venue=gigs_dict[gig]['venue'],
                          pay=gigs_dict[gig]['pay'], trip_origin=gigs_dict[gig]['trip_origin'],
                          comment=gigs_dict[gig]['comment'])
        except KeyError as ke:
            print('')
            print('First try Key error: {}'.format(ke))
            print('Arg 0: {}'.format(ke.args[0]))
            print('')
            try:
                add_gig = Gig(gig_date=gigs_dict[gig]['date'], band=gigs_dict[gig]['band'], venue=gigs_dict[gig]['venue'],
                              pay=gigs_dict[gig]['pay'], trip_origin='2517 Commonwealth',
                              comment=gigs_dict[gig]['comment'])
            except KeyError as ke2:
                print('')
                print('2nd try Key error: {}'.format(ke2))
                print('Arg 0: {}'.format(ke2.args[0]))
                print('')
                add_gig = Gig(gig_date=gigs_dict[gig]['date'], band=gigs_dict[gig]['band'], venue=gigs_dict[gig]['venue'],
                              pay=gigs_dict[gig]['pay'], trip_origin='2517 Commonwealth',
                              comment=None)

        db.session.add(add_gig)
        db.session.commit()


# distances = process_distances_input_csv('distances.csv')
# distances_dict = distances.return_venue_dictionary()
#
# populate_venue_distance_data(distances_dict)

# distances.print_out_mileage_list()
# populate_trial_fake_gig_data()

# gigs_object = process_gig_input_csv('gigs_2018.csv')
# gigs_dictionary = gigs_object.return_gigs_dictionary()
# populate_gig_data(gigs_dictionary)
#
# gigs_object = process_gig_input_csv('gigs_2014.csv')
# gigs_dictionary = gigs_object.return_gigs_dictionary()
# populate_gig_data(gigs_dictionary)
#
# gigs_object = process_gig_input_csv('gigs_2016.csv')
# gigs_dictionary = gigs_object.return_gigs_dictionary()
# populate_gig_data(gigs_dictionary)

# print_gigs_dictionary()

# gigs_object.print_out_gig_by_gig()
