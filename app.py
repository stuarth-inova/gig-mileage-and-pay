#!/usr/bin/env python

from flask import Flask, escape, url_for, render_template
import calc_miles_and_pay
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc
from sqlalchemy import desc
from datetime import date
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Gig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gig_date = db.Column(db.Date, unique=False, nullable=False)
    venue = db.Column(db.String(120), unique=False, nullable=False)
    pay = db.Column(db.Float, unique=False, nullable=True)
    band = db.Column(db.String(60), unique=False, nullable=False)
    trip_origin = db.Column(db.String(30), unique=False, nullable=True)
    comment = db.Column(db.String(250), unique=False, nullable=True)

    def __repr__(self):
        return '<Gig %r>' % self.id


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue = db.Column(db.String(80), unique=True, nullable=False)
    rt_miles_from_commonwealth = db.Column(db.Float, unique=False, nullable=True)
    rt_miles_from_dry_bridge = db.Column(db.Float, unique=False, nullable=True)
    city = db.Column(db.String(30), unique=False, nullable=True)

    def __repr__(self):
        return '<Venue %r>' % self.venue


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello')
@app.route('/hello/<name>')
@app.route('/hello/<name>/')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/gigs')
def gigs():
    return render_template('gigs.html')


@app.route('/summary')
def no_input_gigs_error():
    env_err = 'Please append GIGS data CSV file in path after ' \
              'summary. E.g. "http://my_url:my_port/summary/gigs_2019.csv"'
    return render_template('error.html', exception=env_err)


@app.route('/summary/<input_gigs>')
@app.route('/summary/<input_gigs>/<verbose_flag>')
def summary(input_gigs, verbose_flag=None):
    input_distances = 'distances.csv'

    if verbose_flag:
        verbose = True
    else:
        verbose = False

    try:
        annualGigs = calc_miles_and_pay.process_gig_input_csv(input_gigs)
    except EnvironmentError as env_err:    # Almost certainly File Not Found
        return render_template('error.html', input_file=input_gigs, exception=env_err)

    venue_distance = calc_miles_and_pay.process_distances_input_csv(input_distances)

    miles_sum, pay_sum, num_gigs, gig_data_file, venues_unmatched = calc_miles_and_pay.gig_pay_distance_summary(
        input_gigs, annualGigs, venue_distance, verbose)

    if verbose:
        # unique_band_list = annualGigs.unique_band_list()
        # miles_per_venue_list = calc_miles_and_pay.mileage_per_venue(annualGigs, venue_distance)

        # Strip year out of filename
        year = re.search(r'\d\d\d\d', input_gigs).group()
        print('Year is {} and type {}'.format(year, type(year)))
        try:
            unique_band_list, miles_per_venue_list = give_unique_lists_bands_and_venues(year)
        except ValueError as val_err:
            return render_template('error.html', exception=val_err)
    else:
        unique_band_list = []
        miles_per_venue_list = []

    return render_template('summary.html', num_gigs=num_gigs, miles=miles_sum, pay=pay_sum, data_file=gig_data_file,
                           unmatched_venue_list=venues_unmatched, unique_band_list=unique_band_list,
                           miles_per_venue_list=miles_per_venue_list)


def give_unique_lists_bands_and_venues(year):
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)

    band_list = [gig.band for gig in Gig.query.order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).
                 filter(Gig.gig_date <= end)]
    # venue_list = [gig.venue for gig in Gig.query.order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).
    #               filter(Gig.gig_date <= end)]
    venue_list = give_miles_per_venue(year)

    return set(band_list), venue_list


def give_miles_per_venue(year):
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)

    venue_list = [(gig.trip_origin, gig.venue) for gig in db.session.query(Gig.trip_origin, Gig.venue)
                  .order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).filter(Gig.gig_date <= end)]

    by_venue_tracking_dict = {}
    for origin, gig_venue in venue_list:
        try:
            if origin == "2517 commonwealth":
                rt_miles = db.session.query(Venue.rt_miles_from_commonwealth).filter(Venue.venue == gig_venue).first()[0]
            elif origin == "741 dry bridge":
                rt_miles = db.session.query(Venue.rt_miles_from_dry_bridge).filter(Venue.venue == gig_venue).first()[0]
            else:
                print("Origin key didn't match!!")
                raise KeyError
        except KeyError as key_error:
            # print('Mileage not tracked for venue {}'.format(venue))
            if gig_venue not in by_venue_tracking_dict.keys():
                by_venue_tracking_dict.update({gig_venue: 'Not matched for mileage'})
        else:
            if gig_venue in by_venue_tracking_dict.keys():
                by_venue_tracking_dict[gig_venue] += rt_miles
            else:
                by_venue_tracking_dict.update({gig_venue: rt_miles})
            # print('Cumulative distance for {} is {:0.1f} miles r/t'.format(venue, by_venue_tracking_dict[venue]))

    miles_per_venue_list = []
    for venue in by_venue_tracking_dict:
        if by_venue_tracking_dict[venue] == 'Not matched for mileage':
            miles_per_venue_list.append('{: <20}  - Not matched for mileage'.format(venue))
        else:
            miles_per_venue_list.append('{: <20}  - Cumulative r/t mileage: {:0.1f}'.
                                        format(venue, by_venue_tracking_dict[venue]))

    # miles_per_venue_list = [("Millers", 9.8), ("Ix", 11.1), ("Basic City", 34.0)]

    return miles_per_venue_list


@app.route('/gigs/<gig_year>')
def gig_details(gig_year):
    try:
        return render_template('gig_details.html', data_file=gig_year, gig_dict=db_printable_gig_list(gig_year))
    except ValueError as val_err:
        return render_template('error.html', exception=val_err)


def db_printable_gig_list(year):
    """
    Try to reproduce the clean dump in a list to feed the templates pulling from the DB

    Returns the default list of gigs for the year specified; this list "just worked" in my existing template - cool!
    :return:
    """
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)

    print_gigs = Gig.query.order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).filter(Gig.gig_date <= end)

    return print_gigs


if __name__ == "__main__":
    app.run()
