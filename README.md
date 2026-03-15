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

## Running Tests

Tests use an isolated in-memory SQLite database -- they never touch your `test.db` production data. No need to start the Flask server first; the test suite handles everything automatically (including spinning up a live server for the browser tests).

### Prerequisites (one time)

```bash
pipenv install --dev
pipenv run playwright install chromium
```

### Run all tests

```bash
pipenv run pytest tests/ -v
```

### Run specific test files

```bash
pipenv run pytest tests/test_routes.py -v         # route response tests
pipenv run pytest tests/test_forms.py -v           # form submission tests
pipenv run pytest tests/test_calculations.py -v    # mileage/pay calculation tests
pipenv run pytest tests/test_e2e.py -v             # Playwright browser tests
```

### Run a single test

```bash
pipenv run pytest tests/test_calculations.py::test_annual_summary_2014 -v
```

## To Do
* Allow users to selectively update gig mileage values for venues
* Edit gig details
* Display gig start values
* Validate gig submission uniqueness constraint