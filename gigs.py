#!/usr/bin/env python

from datetime import date

"""
Gigs object that holds all of one year's gigs
    Main key is dates of gig event
    Secondary key in each gig even't dict:
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
            #gig_key = str(gig_index)
            gig_date_list = gig_event[2].split('/')
            gig_day = int(gig_date_list[1])
            gig_month = int(gig_date_list[0])
            gig_year = int(gig_date_list[2]) + 2000
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
                        
                    # Handle empty trip_origin here - but first try to handle on output method
                    if new_key == 'trip_origin':
                        if not gig_event[index]:
                            self.gigs_dict[gig_index][new_key] = '2517 commonwealth'
                        else:
                            self.gigs_dict[gig_index][new_key] = gig_event[index]
                        # print('trip origin value after processing: {}'.format(self.gigs_dict[gig_event[2]][new_key]))
                    elif new_key == 'date':
                        self.gigs_dict[gig_index][new_key] = gig_date
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
            
            gig_index = gig_index + 1
              
    def print_out_gig_by_gig(self):
        print('')
        print('** Gig-by-gig report **')
        print('-----------------------')
        for key in sorted(self.gigs_dict):
            #print("Key index:{}".format(key))
            print('On {} at {}:'.format(self.gigs_dict[key]['date'], self.gigs_dict[key]['venue']))
            try:
                print('    pay: {}; band: {}; origin: {}'.format(self.gigs_dict[key]['pay'], self.gigs_dict[key]['band'], self.gigs_dict[key]['trip_origin']))
            except KeyError as expected_error:
                print('    pay: {}; band: {}; origin: {}'.format(self.gigs_dict[key]['pay'], self.gigs_dict[key]['band'], '2517 commonwealth'))
            try:
                if self.gigs_dict[key]['comment']:
                    print('    comment if any: {}'.format(self.gigs_dict[key]['comment']))
            except KeyError as no_comment_err:
                pass
        print('')
        
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
    
    # def rt_total_miles(self, venue, trip_origin='2517 commonwealth'):
    #     if trip_origin == '2517 commonwealth':
    #         return self.gig_dict[venue]['round_trip_commonwealth']
    #     elif trip_origin == '741 dry bridge':
    #         return self.gigs_dict[venue]['round_trip_dry_br']
