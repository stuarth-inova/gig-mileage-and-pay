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
        sys.exit()


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
                

# ToDo: actually implement this using the new plumbing - should be easy?
def print_output_dict(out_file, out_dict):
    """Prints our special dictionary to specified output file, where keys are topics, and
    values are lists of subscribers to that topic, with sorted keys (sorted topics)"""

    try:
        with open(out_file, "w") as sort_out:
            # This sorts the dictionary keys (topics) while outputting the topics and subs
            for key in sorted(out_dict):
                sort_out.write(key)
                for line in out_dict[key]:
                    sort_out.write(line)
    except IOError as err:
        print('Problem opening/writing to output file ' + str(out_file) + '. Gave error: ' + str(err))


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


def main(argv):
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = 'Caluclates annual gig mileage from two .csv files: one of gigs, the other of mileage to each gig.',
        epilog = """Example usage:
python calc-mileage.py -g file_o_gigs.csv -m file_o_roundtrip_distance_to_gigs.csv -o output_mileage.txt""")
    parser.add_argument("-g", "--gigs_file", action = "store", dest = "gigs_csv", required = True,
                        help = "CSV format file of gigs for a period of time - 1 year for taxes")
    parser.add_argument("-m", "--distances_file", action = "store", dest = "dists_csv", required = True,
                        help = "CSV format file of distances to gig locations")
    parser.add_argument("-o", "--output_file", action = "store", dest = "outfile", required = False,
                        help = "Output file name, can include path or will output locally")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", required = False,
                        help = "Provide additional output and computations")
    
    args = parser.parse_args()

    # Create value for outfile if none passed in - this needs more help to handle paths arbitrarily
    if not args.outfile:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        args.outfile = dir_path + '/mileage_out.txt'
            
    #print("Gigs file: " + args.gigs_csv)
    #print ("Distances file: " + args.dists_csv)
    #print ("Output file: " + args.outfile)

    # Read in csv files
    raw_gigs_list=read_raw_csv_file(args.gigs_csv)
    raw_dists=read_raw_csv_file(args.dists_csv)

    distances = remove_blank_elements(raw_dists)
    gigs_list = remove_blank_elements(raw_gigs_list)
    
    #for line in gigs_list:
    #    print('{}'.format(line))

    # First row in ea file is a header, save them for later    
    gig_hdr = gigs_list.pop(0)
    dist_hdr = distances.pop(0)

    # Create venue-distances object
    venue_distance = VenueMileage(distances, dist_hdr)
#    venue_distance.print_out_mileage_list()
    
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
    annualGigs = Gigs(gigs_list, gig_hdr)
    # annualGigs.print_out_gig_by_gig()
    # print('')

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
            print('{}'.format(band))

        # ToDo: Combine this list of unique venues with the per venue mileage list w/ unmatched venues as 'unmatched'
        print('\nUnique set of venues from {} is:'.format(args.gigs_csv))
        for venue in unique_venue_list:
            print('{}'.format(venue))
        print('')

        miles_per_venue_dict = mileage_per_venue(annualGigs, venue_distance)
        print('Cumulative mileage per gig that matched the distance list')
        print('---------------------------------------------------------')
        for venue in miles_per_venue_dict:
            print('Venue: {: <20}  - Cumulative r/t mileage: {:0.1f}'.format(venue, miles_per_venue_dict[venue]))

    # Section computes total mileage and pay
    gigs = annualGigs.gig_keys()
    miles_sum = 0.0
    pay_sum = 0.0
    for gig in gigs:
        try:
            miles_sum += float(venue_distance.rt_miles(annualGigs.gig_venue(gig), annualGigs.gig_origin(gig)))
        except KeyError as bad_key:
            if args.verbose:
                print('The venue "{}" was NOT matched in the distance file, not included in mileage total.'.format(annualGigs.gig_venue(gig)))
                print('    The index of the problem is: {}\n'.format(bad_key))
            else:
                pass

        pay_sum += float(annualGigs.gig_pay(gig))
    
    print('\nFor {} - Number of gigs: {}, Miles: {:0.1f}; Pay: {:0.2f}'.format(args.gigs_csv, len(gigs), miles_sum, pay_sum))
    print('-----------------------------------------')


if __name__ == '__main__':
    main(sys.argv[1:])

