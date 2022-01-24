# gig-mileage-and-pay
Simple python app that takes a CSV of events, or gigs, for a year and computes mileage and money made.
Also must provide a distances file with round trip distances to the location of each gig from your starting point.

(That's how it started...)

## legacy scripts
* `calc-mileage-old.py`
* `calc-mileage.py`
* `calc_miles_and_pay.py`

Legacy scripts that read .csv files with gigs (usually a year's worth), and a file of round-trip distances. It basically computes pay and mileage for the year, with a few other options.

## fast flask app
* pipenv shell
* flask run

Hit the local webserver at

[http://localhost:5000/]()

pycharm setup for the repo
