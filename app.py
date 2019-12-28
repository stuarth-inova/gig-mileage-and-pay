#!/usr/bin/env python

from flask import Flask, escape, url_for, render_template
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
