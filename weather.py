import os
import logging
import json
import time
from collections import namedtuple

import requests


Weather = namedtuple(
    'Weather', ['icon', 'temp', 'temp_min', 'temp_max', 'wind'])


def cache_path():
    pth_cache = os.path.expanduser("~/.clock/cache/")
    if not os.path.exists(pth_cache):
        os.makedirs(pth_cache)
    return os.path.join(pth_cache, "darksky.json")


def load_cached():
    fn_cache = cache_path()

    if not os.path.exists(fn_cache):
        return None

    # get last modified time for cache...
    ts_cache = os.path.getmtime(fn_cache)
    # refresh every 10 minutes
    if ts_cache is not None:
        now = time.time()
        if (now - ts_cache) > (60*10):
            return None

    logging.info("Loading forecast from cache file: %s" % fn_cache)
    with open(fn_cache) as fp:
        return json.load(fp)

    return None


def fetch_forecast():
    logging.info(
        "Getting a fresh forecast from the https://api.darksky.net/forecast...")

    try:
        r = requests.get(
            "https://api.darksky.net/forecast/{}/{}".format(
                os.environ.get("DARKSKY_KEY"),
                os.environ.get("LAT_LON")
            ),
            params={
                "units": "si",
                "exclude": "minutely,hourly,alerts,flags"
            }
        )

        # write forecast data to cache
        fn_cache = cache_path()
        with open(fn_cache, 'wb') as fp:
            fp.write(r.text.encode('utf-8'))

        return r.json()

    except Exception as e:
        logging.info("No connection to the weather server")
        logging.exception(e)

    return None


def load_forecast():
    # start from cached data
    forecast_data = load_cached()

    # no forecast has been cached yet
    if forecast_data is None:
        forecast_data = fetch_forecast()

    return forecast_data


def get_weather():
    forecast_data = load_forecast()
    if forecast_data is None:
        return None

    d = forecast_data["daily"]["data"][0]
    temp_min = d["temperatureMin"]
    temp_max = d["temperatureMax"]

    c = forecast_data['currently']
    return Weather(
        icon=c['icon'],
        temp=c['temperature'],
        temp_min=temp_min,
        temp_max=temp_max,
        wind=c['windSpeed']
    )


if __name__ == '__main__':
    print(get_weather())
