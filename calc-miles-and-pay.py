#!/usr/bin/env python

import os, sys
import argparse
import csv
from venue import VenueMileage
from gigs import Gigs
from decimal import *
from datetime import date


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


def dict_from_hdrs_and_data(fillin_dict, hdr_list, data_list):
    for ind, header in enumerate(hdr_list):
        if not header in fillin_dict:
            fillin_dict[header] = [item[ind] for item in data_list]
        else:    
            fillin_dict[header].append([item[ind] for item in data_list])
    
    # Get rid of the 'R/T Miles' key and data, it's not supported any more in favor of distances file
    try:
        del fillin_dict['R/T Miles'.lower()]
    except KeyError:
        pass


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
    if args.outfile == None:
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
    
    """Gigs has the 'schema' as follows:
        Band - index 0
        Venue - index 1
        Date - index 2
        Pay in $ - index 3
        Round Trip Mileage - index 4 (optional - no longer used)
        Trip Origin - index 5 - only valid choices are "2517 commonwealth" or "741 dry bridge" - no arg given, uses 2517 commonwealth r/t mileage.
    """

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
  
    #Map these "columns" into "rows" by making a dictionary using the header row as keys

    ##gigs_dict = {}
    ##dict_from_hdrs_and_data(gigs_dict, gig_hdr, gigs_list)

    # Use new Gigs object
    print('Instantiating Gigs object...')
    annualGigs = Gigs(gigs_list, gig_hdr)
    #annualGigs.print_out_gig_by_gig()
    #print('')

## Output of the old gigs_dict approach
    ##print('')
    ##print('Old gig_dict method results')
    ##print('---------------------------')
    
    #print('')
    #print(gigs_dict['venue'])
    #for key in gigs_dict:         #New and improved w/python 3
    #    print('Key: {}'.format(key))
    
    ##print('')
 
    ## demonstrate some simple comps using the power of the dictionary of lists and distance dict
    ##if args.verbose:
        ##for key in gigs_dict:
            ##if key == 'Band'.lower() or key == 'Venue'.lower():
                ##if key == 'Band'.lower():
                    ##print('Unique set of bands I play with is:')
                ##else:
                    ##print('Unique venues I played at were:')
                ##for unique_element in sorted(set(gigs_dict[key])):
                    ##print("{}".format(unique_element))
                ##print('')

    ### Get just the total sum of mileage from the gigs file

    ### Create a count per venue
    ##venue_count = []
    ##for gig_venue in gigs_dict['venue']:
        ##num_times_at_venue = gigs_dict['venue'].count(gig_venue)
        ###print 'Played {0} times at {1}'.format(num_times_at_venue, gig_venue)
        ##venue_count.append((gig_venue, num_times_at_venue))

    ### This is the method using the mileage file input, in the venue_distance object, instead of the r/t data in the gigs file.
    ###
    ### Multiply this count by mileage per venue
    ##total_matched_mileage = 0
    ##unique_ven_count = set(venue_count)
    ##unmatched_venue_msgs = []
#    print unique_ven_count
    ##for unique_venue in unique_ven_count:
        ##venue_matched = False
#        print 'Played at {0} {1} time(s)'.format(unique_venue[0], unique_venue[1])

# Old way doesn't work with different gig origins for the same venue in a year
        ##try:
            ### Hard-coded for the old place; up until 2018 that was the sole gig origin
            ##total_miles = Decimal(unique_venue[1]) * Decimal(venue_distance.rt_miles(unique_venue[0], '2517 commonwealth'))
        ##except KeyError as err:
            ##print('The venue "{}" was NOT matched in the distance file.'.format(unique_venue[0]))
            ##print('The key error returned was: {}'.format(err))
            ##unmatched_venue_msgs.append('{}'.format(unique_venue[0]))
        ##except Exception as unknown_err:
            ##print('Math error on empty value for venue: {}'.format(unique_venue[0]))
            ##print('Actual error: {}'.format(unknown_err))
            ##sys.exit('Exiting after catching un-expected error')
        ##else:
            ##print('Mileage total for venue {}: {}'.format(unique_venue[0], total_miles))
            ##total_matched_mileage += total_miles

    ### Spit out results
    ##print('\nTotal number of gigs played: {}'.format(len(gigs_dict['Venue'.lower()])))
    ##print('\nTotal matched mileage is {}'.format(total_matched_mileage))
    ##print('\nSum of pay is {}'.format(sum(map(Decimal, gigs_dict['pay']))))
    ##print('')
    ##print('Listing of unmatched venues: ')
    ##if len(unmatched_venue_msgs) > 0:
        ##for listing in unmatched_venue_msgs:
            ##print("{}".format(listing))
    ##else:
        ##print("No unmatched venues to list")
        
    ##print('---------------------------')

# Get numbers out of the new approach    
    print('')
    print('*** Values from the new Gigs object!! ***')
    print('-----------------------------------------')

    # Section computes mileage per venue
    list_of_venues_and_origins = annualGigs.list_of_venues_and_origins()
    by_venue_tracking_dict = {}
    for venue, origin in list_of_venues_and_origins:
        # print(venue, origin)
        try:
            rt_miles = float(venue_distance.rt_miles(venue, origin))
        except KeyError as keyError:
            # print('Mileage not tracked for venue {}'.format(venue))
            pass
        else:
            if venue in by_venue_tracking_dict.keys():
                by_venue_tracking_dict[venue] += rt_miles
            else:
                by_venue_tracking_dict.update({venue: rt_miles})
            # print('Cumulative distance for {} is {:0.1f} miles r/t'.format(venue, by_venue_tracking_dict[venue]))

    for venue in by_venue_tracking_dict:
        print('Venue: {: <20}  - Cumulative r/t mileage: {:0.1f}'.format(venue, by_venue_tracking_dict[venue]))

    # Unique list of bands and venues for the year - actually make a method on gigs object to return sets
    if args.verbose:
        unique_band_list = annualGigs.unique_band_list()
        unique_venue_list = annualGigs.unique_venue_list()

        print('\nUnique set of bands from {} is:'.format(args.gigs_csv))
        for band in unique_band_list:
            print('{}'.format(band))

        print('\nUnique set of venues from {} is:'.format(args.gigs_csv))
        for venue in unique_venue_list:
            print('{}'.format(venue))

        print('')

    # Section computes total mileage and pay
    gigs = annualGigs.gig_keys()
    miles_sum = 0.0
    pay_sum = 0.0
    for gig in gigs:
        try:
            miles_sum += float(venue_distance.rt_miles(annualGigs.gig_venue(gig), annualGigs.gig_origin(gig)))
        except KeyError as bad_key:
            print('The venue "{}" was NOT matched in the distance file, not included in mileage total.'.format(annualGigs.gig_venue(gig)))
            print('    The index of the problem is: {}\n'.format(bad_key))

        pay_sum += float(annualGigs.gig_pay(gig))
    
    print('For {} - Number of gigs: {}, Miles: {:0.1f}; Pay: {:0.2f}'.format(args.gigs_csv, len(gigs), miles_sum, pay_sum))
    print('-----------------------------------------')


if __name__ == '__main__':
    main(sys.argv[1:])

