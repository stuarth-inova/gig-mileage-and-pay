#!/usr/bin/env python

import os, sys
import argparse
import csv
from venue import VenueMileage
from gigs import Gigs
from decimal import *


def read_raw_csv_file(csv_file):
    """Read in csv file line by line"""
    input_list = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                row_lower = [entry.lower() for entry in row]
                input_list.append(row_lower)
                
            return input_list
    except EnvironmentError as err:
        print('Problem opening or reading input csv file {}. Gave error: {} \n'.format(csv_file, err))
        #sys.exit()
        raise


def remove_blank_elements(parsed_csv_file):
    """remove records from CSV input where all elements are empty"""
    new_list = []
    for line in parsed_csv_file:
        has_data = False
        for element in line:
            if str(element).strip():
                has_data = True
        if has_data:
            new_list.append(line)
    return new_list


def mileage_per_venue(gigs_object, distances):
    """
    Computes mileage per venue
    :return: dictionary where keys are unique venue list and values are total mileage for that venue
    """
    list_of_venues_and_origins = gigs_object.list_of_venues_and_origins()
    by_venue_tracking_dict = {}
    for venue, origin in list_of_venues_and_origins:
        # print(venue, origin)
        try:
            rt_miles = float(distances.rt_miles(venue, origin))
        except KeyError as key_error:
            # print('Mileage not tracked for venue {}'.format(venue))
            pass
        else:
            if venue in by_venue_tracking_dict.keys():
                by_venue_tracking_dict[venue] += rt_miles
            else:
                by_venue_tracking_dict.update({venue: rt_miles})
            # print('Cumulative distance for {} is {:0.1f} miles r/t'.format(venue, by_venue_tracking_dict[venue]))

    return by_venue_tracking_dict


def gig_pay_distance_summary(gig_filename, annualGigs, venue_distance, verbose_flag):
    """
    Section computes total mileage, pay, number of gigs, and also returns raw input file
    :return: miles_sum, pay_sum, num_gigs, gig_filename
    """
    curr_gigs = annualGigs.gig_keys()
    miles_sum = 0.0
    pay_sum = 0.0
    unmatched_venues = []
    for gig in curr_gigs:
        try:
            miles_sum += float(venue_distance.rt_miles(annualGigs.gig_venue(gig), annualGigs.gig_origin(gig)))
        except KeyError as bad_key:
            if verbose_flag:
                print('The venue "{}" was NOT matched in the distance file, not included in mileage total.'.format(annualGigs.gig_venue(gig)))
                print('    The index of the problem is: {}'.format(bad_key))
                unmatched_venues.append(annualGigs.gig_venue(gig))
            else:
                pass

        pay_sum += float(annualGigs.gig_pay(gig))
        num_gigs = len(curr_gigs)

    return miles_sum, pay_sum, num_gigs, gig_filename, unmatched_venues


def process_gig_input_csv(raw_input_file):
    """
    Take raw 'gigs' input CSV file and returns populated gig object
    :param raw_input_file: CSV of gigs, pay, and origin
    :return: Populated 'Gigs' object
    """
    raw_gigs_list = read_raw_csv_file(raw_input_file)
    gigs_list = remove_blank_elements(raw_gigs_list)

    # for line in gigs_list:
    #    print('{}'.format(line))

    gig_hdr = gigs_list.pop(0)

    # Handle some text label modifications ToDo: add fuzzy name matching module for venues
    for gig in gigs_list:
        gig[1] = gig[1].replace('Millers'.lower(), "Miller's".lower())
        gig[1] = gig[1].replace("Glass House private birthday Tim Braden's wife".lower(), "Glass House".lower())
        gig[1] = gig[1].replace("GlassHouse".lower(), "Glass House".lower())
        gig[1] = gig[1].replace('Cowfest'.lower(), 'Alder Creek'.lower())
        gig[1] = gig[1].replace('WTJU Benefit'.lower(), 'WTJU'.lower())
        gig[1] = gig[1].replace('Mntn Cove Music Festival'.lower(), 'Mountain Cove Winery'.lower())
        gig[1] = gig[1].replace('The Haven Help Betty Benefit'.lower(), 'The Haven'.lower())
        gig[1] = gig[1].replace("Shebeen Cullen's grad pty".lower(), 'the shebeen')

    # Use new Gigs object
    gigs_object = Gigs(gigs_list, gig_hdr)
    # annualGigs.print_out_gig_by_gig()
    # print('')

    return gigs_object


def process_distances_input_csv(raw_distances_file):
    """
    Take raw 'distances' input CSV and returns populated VenueMileage object
    :param raw_distances_file: CSV of venues and round-trip distances
    :return: Populated "VenueMileage" object
    """
    raw_dists = read_raw_csv_file(raw_distances_file)
    distances = remove_blank_elements(raw_dists)

    dist_hdr = distances.pop(0)

    # Create venue-distances object
    venues_object = VenueMileage(distances, dist_hdr)

    # venues_object.print_out_mileage_list()

    return venues_object


def main(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Caluclates annual gig mileage from two .csv files: one of gigs, the other of mileage to each gig.',
        epilog="""Example usage:
python calc-mileage.py -g file_o_gigs.csv -m file_of_roundtrip_distance_to_gigs.csv""")
    parser.add_argument("-g", "--gigs_file", action="store", dest="gigs_csv", required=True,
                        help="CSV format file of gigs for a period of time - 1 year for taxes")
    parser.add_argument("-m", "--distances_file", action="store", dest="dists_csv", required=True,
                        help="CSV format file of distances to gig locations")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", required=False,
                        help="Provide additional output and computations")
    
    args = parser.parse_args()

    # Use raw CSV files' data to populate to instantiate both main classes
    annualGigs = process_gig_input_csv(args.gigs_csv)
    venue_distance = process_distances_input_csv(args.dists_csv)

# Get numbers out of the new approach - now the only approach
    print('')
    print('*** Gigs from {} ***'.format(args.gigs_csv))
    print('-----------------------------------------')
    # Unique list of bands and venues for the year
    if args.verbose:
        unique_band_list = annualGigs.unique_band_list()
        unique_venue_list = annualGigs.unique_venue_list()

        print('Unique set of bands from {} is:'.format(args.gigs_csv))
        for band in unique_band_list:
            print('     {}'.format(band))

        print('\nUnique set of venues from {} is:'.format(args.gigs_csv))
        for venue in unique_venue_list:
            print('     {}'.format(venue))
        print('')

        miles_per_venue_dict = mileage_per_venue(annualGigs, venue_distance)
        print('Cumulative mileage per gig that matched the distance list')
        print('---------------------------------------------------------')
        for venue in miles_per_venue_dict:
            print('Venue: {: <20}  - Cumulative r/t mileage: {:0.1f}'.format(venue, miles_per_venue_dict[venue]))

    # Use function for annual gig summary stats, this will make calling it for Flask output easier
    miles_sum, pay_sum, num_gigs, gig_data_file, venues_not_matched = gig_pay_distance_summary(args.gigs_csv,
                                                                                               annualGigs,
                                                                                               venue_distance,
                                                                                               args.verbose)

    if args.verbose:
        print('\n<<< Totals >>>')
        print('-----------------------------------------')
    print('For {}: {} gigs; {:0.1f} miles; ${:0.2f} pay'.format(gig_data_file, num_gigs, miles_sum, pay_sum))
    print('-----------------------------------------')


if __name__ == '__main__':
    main(sys.argv[1:])

