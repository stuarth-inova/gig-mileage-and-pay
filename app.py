#!/usr/bin/env python

from flask import Flask, escape, url_for, render_template
import calc_miles_and_pay
import sys
import argparse
import csv
from venue import VenueMileage
from gigs import Gigs

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello')
@app.route('/hello/<name>')
@app.route('/hello/<name>/')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/members')
@app.route('/members/<path:username>')
def members(username=None):
    if username:
        print("triggered strip")
        username = username.strip("/")
    return render_template('members.html', username=username)


@app.route('/gigs')
def gigs():
    return render_template('gigs.html')


@app.route('/summary')
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
    except EnvironmentError as env_err:
        return render_template('error.html', input_file=input_gigs, exception=env_err)

    venue_distance = calc_miles_and_pay.process_distances_input_csv(input_distances)

    miles_sum, pay_sum, num_gigs, gig_data_file = calc_miles_and_pay.gig_pay_distance_summary(input_gigs,
                                                                            annualGigs, venue_distance, verbose)

    return render_template('summary.html', num_gigs=num_gigs, miles=miles_sum, pay=pay_sum, data_file=gig_data_file)


if __name__ == "__main__":
    app.run()
