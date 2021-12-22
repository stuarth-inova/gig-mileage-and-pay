#!/usr/bin/env python

from flask import Flask, escape, url_for, render_template, request
import calc_miles_and_pay
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc
from sqlalchemy import desc
from datetime import date
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/stuartholme/gig-mileage-and-pay/test.db'
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
@app.route('/gigs/')
def gigs():
    return render_template('gigs.html')


@app.route('/gigs/<gig_year>')
def gig_details(gig_year):
    try:
        return render_template('gig_details.html', data_file=gig_year, gig_dict=db_printable_gig_list(gig_year))
    except ValueError as val_err:
        return render_template('error.html', exception=val_err)


@app.route('/gigs/submit')
def enter_new_gig():
    """
    Renders a form for entry of gig data
    :return:
    """
    return render_template('submit_new_gig.html')


@app.route('/gigs/new_gig_data', methods=['POST', 'GET'])
def submit_new_gig():
    """
    Process form data for entry of new gig
    :return:
    """
    if request.method == 'POST':
        result = request.form
        print('')
        print('Contents of request.items:')
        for item in result.items():
            print('Item: {}  - of type: {}'.format(item, type(item)))
            for element in item:
                print('Element: {}  -of type: {}'.format(element, type(element)))

        return render_template("gig_data_input_echo.html", result=result)
    else:
        return render_template('error.html', exception='Improper form submission! Used "GET" on this route.')


@app.route('/summary')
@app.route('/summary/')
def no_input_gigs_error():
    env_err = 'Please include year in path; ' \
              'e .g. "http://my_url:my_port/summary/2019"'
    return render_template('error.html', exception=env_err)


@app.route('/summary/<year>')
@app.route('/summary/<year>/')
@app.route('/summary/<year>/<verbose_flag>')
def summary(year, verbose_flag=None):
    # ToDo: handle arbitrary year input; later on it gets cast to int and blows up with ValueError
    if verbose_flag:
        verbose = True
    else:
        verbose = False

    miles_sum, pay_sum, num_gigs, gig_data_file, venues_unmatched = annual_gig_pay_miles_summary(year, verbose)

    if verbose:
        try:
            unique_band_list, miles_per_venue_list = give_unique_lists_bands_and_venues(int(year))
        except ValueError as val_err:
            return render_template('error.html', exception=val_err)
    else:
        unique_band_list = []
        miles_per_venue_list = []

    return render_template('summary.html', num_gigs=num_gigs, miles=miles_sum, pay=pay_sum, data_file=gig_data_file,
                           unmatched_venue_list=venues_unmatched, unique_band_list=unique_band_list,
                           miles_per_venue_list=miles_per_venue_list, gigs_url=url_for('gig_details', gig_year=year))


def give_unique_lists_bands_and_venues(year):
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)

    band_list = [gig.band for gig in Gig.query.order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).
                 filter(Gig.gig_date <= end)]
    venue_list = give_miles_per_venue(year)

    return set(band_list), venue_list


def give_miles_per_venue(year):
    """
    Provides a list of text strings, each string represents a venue and the total r/t mileage to that venue for the year
    in question.
    :param year: Sting of year in question
    :return: List of strings for publishing in an output table on the website
    """
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)

    venue_list = [(gig.trip_origin, gig.venue) for gig in db.session.query(Gig.trip_origin, Gig.venue)
                  .order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).filter(Gig.gig_date <= end)]

    by_venue_tracking_dict = {}
    for origin, gig_venue in venue_list:
        try:
            if origin.lower() == "2517 commonwealth":
                rt_miles = db.session.query(Venue.rt_miles_from_commonwealth).filter(Venue.venue == gig_venue).first()[0]
            elif origin.lower() == "741 dry bridge":
                rt_miles = db.session.query(Venue.rt_miles_from_dry_bridge).filter(Venue.venue == gig_venue).first()[0]
            else:
                print("Origin key didn't match!!")
                raise KeyError
        except (KeyError, TypeError):
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

    return miles_per_venue_list


def annual_gig_pay_miles_summary(year, verbose):
    """
    Computes annual summary rollup totals for miles, pay, and number of gigs
    :param year:
    :param verbose:
    :return: mile_total (float), pay_total(float), n_gigs(int), year(str), unmatched_venues(list of str)
    """
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)
    mile_total = 0.0
    pay_total = 0.0
    n_gigs = 0
    unmatched_venues = []

    for gig in Gig.query.order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).filter(Gig.gig_date <= end):
        try:
            if gig.trip_origin.lower() == "2517 commonwealth":
                mile_total += db.session.query(Venue.rt_miles_from_commonwealth).filter(Venue.venue == gig.venue).first()[0]
            elif gig.trip_origin.lower() == "741 dry bridge":
                mile_total += db.session.query(Venue.rt_miles_from_dry_bridge).filter(Venue.venue == gig.venue).first()[0]
            else:
                raise KeyError
        except (KeyError, TypeError):
            if verbose:
                unmatched_venues.append(gig.venue)
            else:
                pass

        pay_total += gig.pay
        n_gigs += 1

    return mile_total, pay_total, n_gigs, year, unmatched_venues


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
