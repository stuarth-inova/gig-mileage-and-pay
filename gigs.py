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
        for gig_event in gig_events_list:
            gig_date_list = gig_event[2].split('/')
            gig_day = int(gig_date_list[1])
            gig_month = int(gig_date_list[0])
            gig_year = int(gig_date_list[2])
            gig_date = date(gig_year, gig_month, gig_day)
            if gig_date not in self.gigs_dict:
                self.gigs_dict[gig_date] = {}
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
                            self.gigs_dict[gig_date][new_key] = '2517 commonwealth'
                        else:
                            self.gigs_dict[gig_date][new_key] = gig_event[index]
                        # print('trip origin value after processing: {}'.format(self.gigs_dict[gig_event[2]][new_key]))
                    elif new_key == 'date':
                        pass
                    elif new_key == 'mileage':
                        pass
                    else:
                        self.gigs_dict[gig_date][new_key] = gig_event[index]
            else:
                print('******')
                print('Somehow a duplicate date name made it into the gigs data file: {}'.format(gig_event[2]))
                print('Unexpected header value in headers list!!')
                print('  ---> {}'.format(headers[index]))
                print('******')
              
    def print_out_gig_by_gig(self):
        print('')
        print('** Gig-by-gig report **')
        print('-----------------------')
        for key in sorted(self.gigs_dict):
            print('On {} at {}:'.format(key, self.gigs_dict[key]['venue']))
            try:
                print('    pay: {}; band: {}; origin: {}'.format(self.gigs_dict[key]['pay'], self.gigs_dict[key]['band'], self.gigs_dict[key]['trip_origin']))
            except KeyError as expected_error:
                print('    pay: {}; band: {}; origin: {}'.format(self.gigs_dict[key]['pay'], self.gigs_dict[key]['band'], '2517 commonwealth'))
            print('    comment if any: {}'.format(self.gigs_dict[key]['comment']))
        print('')
        
    def gig_keys(self):
        """
        Return a list of dates, which are the primary Gigs key
        """
        key_list = []
        for key in sorted(self.gigs_dict):
            key_list.append(key)
            
        return key_list
    
    def gig_pay(self, datekey):
        """
        Return pay for gig date arg
        """
        return self.gigs_dict[datekey]['pay']
    
    def gig_venue(self, datekey):
        """
        Returns the Venue for gig date arg > key for mileage object
        """
        return self.gigs_dict[datekey]['venue']
    
    def gig_origin(self, datekey):
        """
        Returns gig origin for gig date arg
        """
        try:
            return self.gigs_dict[datekey]['trip_origin']
        except KeyError as expected_keyfault:
            return '2517 commonwealth'
    
    # def rt_total_miles(self, venue, trip_origin='2517 commonwealth'):
    #     if trip_origin == '2517 commonwealth':
    #         return self.gig_dict[venue]['round_trip_commonwealth']
    #     elif trip_origin == '741 dry bridge':
    #         return self.gigs_dict[venue]['round_trip_dry_br']
