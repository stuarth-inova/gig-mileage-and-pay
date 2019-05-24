#!/usr/bin/env python

"""
Venue object interrogated by a gig for mileage
"""

class VenueMileage:

    def __init__(self, clean_venue_mileage, headers):
        self.venue_dict = {}
        for clean_venue in clean_venue_mileage:
            if clean_venue[0] not in self.venue_dict:
                self.venue_dict[clean_venue[0]] = {}
                for index in range(1, len(clean_venue)):
                    if headers[index] == 'r/t 2517 commonwealth':
                        new_key = 'round_trip_commonwealth'
                    elif headers[index] == 'r/t 741 dry bridge':
                        new_key = 'round_trip_dry_br'
                    elif headers[index] == 'mileage 1w':
                        new_key = 'one_way'
                    else:
                        new_key = headers[index]  # Handles the City value
                    self.venue_dict[clean_venue[0]][new_key] = clean_venue[index]
            else:
                print('Somehow a duplicate venue name made it into the distances data file: {}'.format(clean_venue[0]))
        
        #print('Just the results for The Brewing Tree...')
        #print('Entire entry: {}'.format(self.venue_dict['brewing tree']))
        #print('R/T from Commonwealth: {}; R/T from Dry Bridge: {}; City: {}'.format(self.venue_dict['brewing tree']['round_trip_commonwealth'], self.venue_dict['brewing tree']['round_trip_dry_br'], self.venue_dict['brewing tree']['city']))
                
    def print_out_mileage_list(self):
        for key in sorted(self.venue_dict):
            print ('{} -- r/t miles: {}; city: {}'.format(key, self.venue_dict[key]['round_trip_commonwealth'], self.venue_dict[key]['city']))
            
    def rt_miles(self, venue, trip_origin='2517 commonwealth'):
        if trip_origin == '2517 commonwealth':
            return self.venue_dict[venue]['round_trip_commonwealth']
        elif trip_origin == '741 dry bridge':
            return self.venue_dict[venue]['round_trip_dry_br']

        
