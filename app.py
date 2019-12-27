from flask import Flask, escape, url_for, render_template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello')
def hello():
    return render_template


@app.route('/members')
def members():
    return "Members"


@app.route('/members/<path:username>')
def get_member(username):
    return "Member: {}".format(escape(username))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
