#!/usr/bin/env python

"""
Gig organizing object to handle a given year's gigs
"""


class GigOrganizer():

    def __init__(self, clean_gig_list, headers):
        self.gig_dict = {}


# ToDo: Output dict of form gig_dict{Date} => Each element points to one dict: keys: Pay, Venue, Band, Trip Origin, Comment
#
# Cycle through gigs (outer keys) and use "Venue" and "Trip Origin" keys to extract R/T Mileage, add to rolling sum; use "Pay" key to get money, add to rolling sum.


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
