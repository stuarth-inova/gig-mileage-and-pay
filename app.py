#!/usr/bin/env python

from flask import Flask, escape, url_for, render_template
import calc_miles_and_pay
from flask_sqlalchemy import SQLAlchemy
from datetime import date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Gig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=False, nullable=False)
    venue = db.Column(db.String(120), unique=False, nullable=False)
    pay = db.Column(db.Float, unique=False, nullable=True)
    band = db.Column(db.String(60), unique=False, nullable=False)
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
        unique_band_list = annualGigs.unique_band_list()
        miles_per_venue_list = calc_miles_and_pay.mileage_per_venue(annualGigs, venue_distance)
    else:
        unique_band_list = []
        miles_per_venue_list = []

    return render_template('summary.html', num_gigs=num_gigs, miles=miles_sum, pay=pay_sum, data_file=gig_data_file,
                           unmatched_venue_list=venues_unmatched, unique_band_list=unique_band_list,
                           miles_per_venue_list=miles_per_venue_list)


@app.route('/gigs/<input_gigs>')
def gig_details(input_gigs):
    try:
        annualGigs = calc_miles_and_pay.process_gig_input_csv(input_gigs)
    except EnvironmentError as env_err:    # Almost certainly File Not Found
        return render_template('error.html', input_file=input_gigs, exception=env_err)

    return render_template('gig_details.html', data_file=input_gigs, gig_dict=annualGigs.printable_gig_list())


if __name__ == "__main__":
    app.run()
