#!/usr/bin/env python

from flask import Flask, escape, url_for, render_template, request, redirect
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
@app.route('/home')
@app.route('/index')
def index():
    return render_template('index.html', unique_years=unique_year_list())


@app.route('/hello')
@app.route('/hello/<name>')
@app.route('/hello/<name>/')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/venue-list')
def venue_list():
    venues = Venue.query.order_by(asc(Venue.venue)).all()
    return render_template('venue_details.html', venue_dict=venues)


@app.route('/gigs')
@app.route('/gigs/')
@app.route('/gig')
def gigs():
    return redirect("/", code=302)


def unique_year_list():
    years = []
    for gig_date in db.session.query(Gig.gig_date):
        years.append(gig_date[0].year)
    unique_years = sorted(set(years))
    return unique_years


@app.route('/gigs/<gig_year>')
def gig_details(gig_year):
    try:
        return render_template('gig_details.html', gig_year=gig_year, gig_dict=db_printable_gig_list(gig_year))
    except ValueError as val_err:
        return render_template('error.html', exception=val_err)


@app.route('/gigs/submit')
def enter_new_gig():
    """
    Renders a form for entry of gig data
    :return:
    """
    venues = Venue.query.order_by(asc(Venue.venue)).all()
    return render_template('submit_new_gig.html', venues_dict=venues)


@app.route('/gigs/new_gig_data', methods=['POST', 'GET'])
def submit_new_gig():
    """
    Process form data for entry of new gig
    :return:
    """
    if request.method == 'POST':
        result = request.form
        gig_date = request.form.get('date')
        venue = request.form.get('venue')
        band = request.form.get('band')
        pay = request.form.get('pay')
        trip_origin = request.form.get('trip_origin')
        comment = request.form.get('comment')

        existing_venue = Venue.query.filter_by(venue=venue.lower()).first()
        if existing_venue is None:
            return redirect(url_for('add_venue'))
        else:
            missing_mileage = False
            if '741 dry bridge' in trip_origin.lower():
                trip_origin = '741 dry bridge'
                print('Value "rt miles" for 741: {}'.format(existing_venue.rt_miles_from_dry_bridge))
                if not existing_venue.rt_miles_from_dry_bridge:
                    missing_mileage = True
                    error_message = 'Mileage for {} not present for 741 Dry Bridge trip origin'.format(venue)

            elif '2517 commonwealth' in trip_origin.lower():
                trip_origin = '2517 commonwealth'
                print('Value "rt miles" for 2517: {}'.format(existing_venue.rt_miles_from_commonwealth))
                if not existing_venue.rt_miles_from_commonwealth:
                    missing_mileage = True
                    error_message = 'Mileage for {} not present for 2517 Commonwealth trip origin'.format(venue)
            else:
                print('Unknown Trip Origin: {}'.format(trip_origin))
                render_template("error.html", exception='Unknown trip origin {} specified!!'.format(trip_origin))

        if missing_mileage:
            return redirect(url_for('update_venue_mileage', problem_venue=venue, message=error_message,
                                    trip_origin=trip_origin))
        else:
            print('Gig date value: {} - Type: {}'.format(gig_date, type(gig_date)))
            try:
                new_gig = Gig(
                    gig_date=date.fromisoformat(gig_date),
                    venue=venue.lower(),
                    pay=pay.strip('$'),
                    band=band,
                    trip_origin=trip_origin,
                    comment=comment
                )
                db.session.add(new_gig)
                db.session.commit()
            except (ValueError, KeyError) as db_error:
                return render_template("error.html", exception=db_error)
            else:
                return render_template("gig_data_input_echo.html", result=result)
    else:
        return render_template('error.html', exception='Improper form submission! Used "GET" on this route.')


@app.route('/venue/update/<problem_venue>/<trip_origin>/<message>')
def update_venue_mileage(problem_venue, trip_origin, message=None):
    """
    Renders a form to add missing round trip mileage from a particular trip origin to an existing venue
    :param problem_venue: Venue missing round-trip mileage from trip_origin
    :param trip_origin: Location user was living when the gig occurred
    :param message: Message specifying issue
    :return:
    """
    return render_template('update_rt_mileage.html', problem_venue=problem_venue, message=message,
                           venue=problem_venue.lower(), trip_origin=trip_origin)


@app.route('/venue/add_venue', methods=['POST', 'GET'])
def add_venue():
    """
    Process form data to enter new venue
    :return:
    """
    if request.method == 'GET':
        return render_template('submit_new_venue.html')

    if request.method == 'POST':
        result = request.form
        venue = request.form.get('venue')
        rt_miles_from_commonwealth = request.form.get('rt_miles_from_commonwealth')
        rt_miles_from_dry_bridge = request.form.get('rt_miles_from_dry_bridge')
        city = request.form.get('city')

        print('ADD venue operation')
        try:
            new_venue = Venue(
                venue=venue.lower(),
                rt_miles_from_commonwealth=rt_miles_from_commonwealth,
                rt_miles_from_dry_bridge=rt_miles_from_dry_bridge,
                city=city,
            )
            db.session.add(new_venue)
            db.session.commit()
        except (ValueError, KeyError) as db_error:
            return render_template("error.html", exception=db_error)
        else:
            return render_template("venue_data_input_echo.html", result=result)
    else:
        return render_template('error.html', exception='Improper form submission! Used "GET" on this route.')


@app.route('/venue/update_venue/<venue>/<trip_origin>', methods=['POST', 'GET'])
def update_venue(venue, trip_origin):
    """
    Process form data to update existing venue with missing round-trip mileage
    :return:

    ToDo: what is this doing? looks like its not hooked up to anything
    """
    if request.method == 'POST':
        result = request.form
        rt_mileage = request.form.get('rt_miles')

        print('***')
        print('in "update_venue" after ingestion: trip origin: {} - r/t mileage: {}'.format(trip_origin, rt_mileage))
        print('and venue: {}'.format(venue))
        print('***')

        print('UPDATE venue operation')
        if '741 dry bridge' in trip_origin.lower():
            updating_venue = Venue.query.filter_by(venue=venue.lower()).update(dict(rt_miles_from_dry_bridge=rt_mileage))
            db.session.commit()
            return render_template('gig_data_input_echo.html', result=result)
        elif '2517 commonwealth' in trip_origin.lower():
            updating_venue = Venue.query.filter_by(venue=venue.lower()).update(dict(rt_miles_from_commonwealth=rt_mileage))
            db.session.commit()
            return render_template('gig_data_input_echo.html', result=result)
        else:
            print('Unknown Trip Origin: {}'.format(trip_origin))
            render_template("error.html", exception='Unknown trip origin {} specified!!'.format(trip_origin))
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

    miles_sum, pay_sum, num_gigs, print_year, venues_unmatched = annual_gig_pay_miles_summary(year, verbose)

    if verbose:
        try:
            unique_band_list, miles_per_venue_list = give_unique_lists_bands_and_venues(int(year))
        except ValueError as val_err:
            return render_template('error.html', exception=val_err)
    else:
        unique_band_list = []
        miles_per_venue_list = []

    return render_template('summary.html', num_gigs=num_gigs, miles=miles_sum, pay=pay_sum, year=print_year,
                           unmatched_venue_list=venues_unmatched, unique_band_list=unique_band_list, verbose=verbose,
                           miles_per_venue_list=miles_per_venue_list, gigs_url=url_for('gig_details', gig_year=year),
                           self_verbose_url=url_for('summary', year=year, verbose_flag='verbose'))


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

    # ToDo: The venue distance checks only check that venue is present, NOT that for a given start there is a mileage value
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)

    venue_list = [(gig.trip_origin, gig.venue) for gig in db.session.query(Gig.trip_origin, Gig.venue)
        .order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).filter(Gig.gig_date <= end)]

    by_venue_tracking_dict = {}
    for origin, gig_venue in venue_list:
        try:
            if origin.lower() == "2517 commonwealth":
                rt_miles = db.session.query(Venue.rt_miles_from_commonwealth).filter(Venue.venue == gig_venue).first()[
                    0]
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
    # ToDo: some gigs don't get mileage cost - right now handled by no RT data in the 'venue' table
    start = date(int(year), 1, 1)
    end = date(int(year), 12, 31)
    mile_total = 0.0
    pay_total = 0.0
    n_gigs = 0
    unmatched_venues = []

    for gig in Gig.query.order_by(asc(Gig.gig_date)).filter(Gig.gig_date >= start).filter(Gig.gig_date <= end):
        try:
            if gig.trip_origin.lower() == "2517 commonwealth":
                mile_total += \
                db.session.query(Venue.rt_miles_from_commonwealth).filter(Venue.venue == gig.venue).first()[0]
            elif gig.trip_origin.lower() == "741 dry bridge":
                mile_total += db.session.query(Venue.rt_miles_from_dry_bridge).filter(Venue.venue == gig.venue).first()[
                    0]
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
