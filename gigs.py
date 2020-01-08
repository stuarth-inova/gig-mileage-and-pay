#!/usr/bin/env python

from datetime import date

"""
Gigs object that holds all of one year's gigs
    Main key is integer index ID of gig event
    Secondary key in each gig even't dict:
        date
        venue
        pay
        band
        comment
        trip_origin - if empty = '2517 Commonwealth'
"""


class Gigs:

    def __init__(self, gig_events_list, headers):
        self.gigs_dict = {}
        gig_index = 0
        for gig_event in gig_events_list:
            gig_date_list = gig_event[2].split('/')
            gig_day = int(gig_date_list[1])
            gig_month = int(gig_date_list[0])
            gig_year = int(gig_date_list[2]) + 2000    # Quite hard-coded for my data...
            gig_date = date(gig_year, gig_month, gig_day)
            if gig_index not in self.gigs_dict:
                self.gigs_dict[gig_index] = {}
                for index in range(0, len(gig_event)):
                    # print('Date: {}); index: {}; value: {}'.format(gig_event[2], index, gig_event[index]))
                    if headers[index] == 'band':
                        new_key = 'band'
                    elif headers[index] == 'venue':
                        new_key = 'venue'
                    elif headers[index] == 'date':
                        new_key = 'date'      # Never add this value to the dict; handled below
                    elif headers[index] == 'pay':
                        new_key = 'pay'
                    elif headers[index] == 'r/t miles':
                        new_key = 'mileage'   # This data is aged out; handle below
                    elif headers[index] == 'trip_origin':
                        new_key = 'trip_origin'
                    elif headers[index] == 'comment':
                        new_key = 'comment'
                    else:
                        new_key = headers[index]
                        
                    # Handle empty trip_origin here
                    if new_key == 'trip_origin':
                        if not gig_event[index]:
                            self.gigs_dict[gig_index][new_key] = '2517 commonwealth'
                        else:
                            self.gigs_dict[gig_index][new_key] = gig_event[index]
                        # print('trip origin value after processing: {}'.format(self.gigs_dict[gig_event[2]][new_key]))
                    elif new_key == 'date':
                        self.gigs_dict[gig_index][new_key] = gig_date
                    # Not using the included mileage data from older gigs.csv files, so just pass this by.
                    elif new_key == 'mileage':
                        pass
                    else:
                        self.gigs_dict[gig_index][new_key] = gig_event[index]
            else:
                print('******')
                print('Somehow a duplicate gig index made it into the gigs data file for this date: {}'.format(gig_event[2]))
                print('Duplicated index for that date')
                print('  ---> {}'.format(gig_index))
                print('******')
            
            gig_index += 1
              
    def print_out_gig_by_gig(self):
        print('')
        print('** Gig-by-gig report **')
        print('-----------------------')
        for key in sorted(self.gigs_dict):
            #print("Key index:{}".format(key))
            print('On {} at {}:'.format(self.gigs_dict[key]['date'], self.gigs_dict[key]['venue']))
            try:
                print('    pay: {}; band: {}; origin: {}'.format(self.gigs_dict[key]['pay'], self.gigs_dict[key]['band'], self.gigs_dict[key]['trip_origin']))
            except KeyError as key_error:
                if key_error.args[0] == 'trip_origin':
                    print('    pay: {}; band: {}; origin: {}'.format(self.gigs_dict[key]['pay'], self.gigs_dict[key]['band'], '2517 commonwealth'))
                else:
                    print('Unexpected key error: {}'.format(key_error))
                    print('Re-throwing error')
                    raise key_error
            try:
                if self.gigs_dict[key]['comment']:
                    print('    comment if any: {}'.format(self.gigs_dict[key]['comment']))
            except KeyError as key_error:
                if key_error.args[0] == 'comment':
                    pass
                else:
                    print('Unexpected key error: {}'.format(key_error))
                    print('Re-throwing error')
                    raise key_error
        print('')

    def printable_gig_list(self):
        """
        Returns a list of dictionaries, rather than a dict of dictionaries as the object is instantiated. For web
        table output
        :return: list of gigs in chronological order (actually key order, counts on chron order input!! ToDO: Fix this
        """
        output_list = []
        for key in sorted(self.gigs_dict):
            output_list.append(self.gigs_dict[key])

        return output_list
        
    def gig_keys(self):
        """
        Return a list of gig_indexes, which are the primary Gigs keys
        """
        key_list = []
        for key in sorted(self.gigs_dict):
            key_list.append(key)
            
        return key_list
    
    def gig_pay(self, gigkey):
        """
        Return pay for gig key arg
        """
        return self.gigs_dict[gigkey]['pay']
    
    def gig_venue(self, gigkey):
        """
        Returns the Venue for gig key arg > key for mileage object
        """
        return self.gigs_dict[gigkey]['venue']
    
    def gig_origin(self, gigkey):
        """
        Returns gig origin for gig key arg
        """
        try:
            return self.gigs_dict[gigkey]['trip_origin']
        except KeyError as expected_keyfault:
            return '2517 commonwealth'

    def list_of_venues_and_origins(self):
        """
        Provide a list of venues, in key order, and the origin of the trip for each of those gigs
        :return: list of tuples; ea tuple is (<venue>, <origin>)
        """
        ordered_venue_origin_list = []
        for key in sorted(self.gigs_dict):
            try:
                ordered_venue_origin_list.append((self.gigs_dict[key]['venue'], self.gigs_dict[key]['trip_origin']))
            except KeyError as key_error:
                if key_error.args[0] == 'trip_origin':
                    ordered_venue_origin_list.append((self.gigs_dict[key]['venue'], '2517 commonwealth'))
                else:
                    print('Unexpected key error: {}'.format(key_error))
                    print('Re-throwing error')
                    raise key_error

        return ordered_venue_origin_list

    def unique_band_list(self):
        """
        Provide a uniques list of bands for the year in question - a set of bands
        :return: list of bands with no duplicates
        """
        non_unique_list = []
        for key in sorted(self.gigs_dict):
            non_unique_list.append(self.gigs_dict[key]['band'])

        return set(non_unique_list)

    def unique_venue_list(self):
        """
        Provide a uniques list of venues for the year in question - a set of bands
        :return: list of venues with no duplicates
        """
        non_unique_list = []
        for key in sorted(self.gigs_dict):
            non_unique_list.append(self.gigs_dict[key]['venue'])

        return set(non_unique_list)

    def return_gigs_dictionary(self):
        return self.gigs_dict

    # def rt_total_miles(self, venue, trip_origin='2517 commonwealth'):
    #     if trip_origin == '2517 commonwealth':
    #         return self.gig_dict[venue]['round_trip_commonwealth']
    #     elif trip_origin == '741 dry bridge':
    #         return self.gigs_dict[venue]['round_trip_dry_br']
