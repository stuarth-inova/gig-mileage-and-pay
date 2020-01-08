#!/usr/bin/env python

from app import db
from app import Gig
from app import Venue
from calc_miles_and_pay import process_gig_input_csv
from calc_miles_and_pay import process_distances_input_csv
from datetime import date

db.create_all()
distances = process_distances_input_csv('distances.csv')

#distances.print_out_mileage_list()

distances_dict = distances.return_venue_dictionary()


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
    gig1 = Gig(date=date(2019, 1, 17), venue='Millers', pay=50, band='Cows')
    gig2 = Gig(date=date(2019,1,25), venue='Ix', pay=80.50, band='Mama Tried')

    db.session.add(gig1)
    db.session.add(gig2)
    db.session.commit()


# populate_venue_distance_data(distances_dict)

# populate_trial_fake_gig_data()

def populate_gig_data(gigs_dict):
    pass


gigs_object = process_gig_input_csv('gigs_2018.csv')
gig_dict = gigs_object.return_gigs_dictionary()

for gig in gig_dict:
    print('{} - type: {}'.format(gig, type(gig)))
    print('{}'.format(gig_dict[gig]))
