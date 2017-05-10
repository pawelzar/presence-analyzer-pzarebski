# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import threading
from json import dumps
from functools import wraps
from datetime import date, datetime, timedelta

from xml.etree import ElementTree

from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def jsonify(func):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(func(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def cache(time):
    """
    Stores function output data for given time in seconds.
    """
    cache.data = {}
    lock = threading.Lock()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            This docstring will be overridden by @wraps decorator.
            """
            now = datetime.now()
            name = func.__name__
            with lock:
                if name in cache.data and \
                   now - cache.data[name]['time'] < timedelta(seconds=time):
                    result = cache.data[name]['data']
                else:
                    result = func(*args, **kwargs)
                    cache.data[name] = {
                        'data': result,
                        'time': now,
                    }
            return result
        return wrapper
    return decorator


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
                data.setdefault(user_id, {})[date] = {
                    'start': start,
                    'end': end,
                }
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

    return data


@cache(600)
def get_data_xml():
    """
    Extracts users data from XML file and groups it by user_id.
    """
    data = ElementTree.parse(app.config['DATA_XML'])
    server = data.find('server')
    link = '{}://{}:{}'.format(
        server.find('protocol').text,
        server.find('host').text,
        server.find('port').text,
    )
    users = {}
    for user in data.find('users'):
        users[int(user.get('id'))] = {
            'name': user.find('name').text,
            'avatar': '{}{}'.format(link, user.find('avatar').text),
        }
    return users


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[] for _ in range(7)]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates interval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_by_weekday_start_end(items):
    """
    Groups start time and end time by weekday.

    It creates structure like this:
    result = [
        {
            'start': [39973, 35827, 31253, 32084, 40358],
            'end': [70900, 61024, 61184, 55828, 70840],
        },
        {
            'start': [33058, 39177, 31018],
            'end': [61740, 71032, 70742],
        }
    ]
    """
    result = [{} for _ in range(7)]  # one dict for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].setdefault('start', []).append(
            seconds_since_midnight(start)
        )
        result[date.weekday()].setdefault('end', []).append(
            seconds_since_midnight(end)
        )
    return result


def group_quarters(items):
    """
    Returns quarters sorted by year and numeral.
    """
    quarters = set()
    for user in items:
        for date in items[user]:
            quarter = date.month // 4 + 1
            quarters.add((date.year, quarter))

    result = {}
    for i, quarter in enumerate(sorted(quarters)):
        result[i] = {
            'year': quarter[0],
            'numeral': quarter[1],
        }
    return result


def overtime_hours_in_quarter(items, quarter):
    """
    Returns overtime hours for every user in given quarter.
    """
    quarter_num = quarter['numeral']
    year = quarter['year']
    seconds_in_hour = 3600
    working_hours = 8 * working_days_in_quarter(year, quarter_num)

    overtime = {user: 0 for user in items.keys()}
    for user, date in items.items():
        for date_key, entry in date.items():
            if date_in_quarter(date_key, year, quarter_num):
                overtime[user] += interval(entry['start'], entry['end'])
        overtime[user] /= seconds_in_hour
        overtime[user] -= working_hours
    return overtime


def working_days_in_quarter(year, quarter):
    """
    Returns working days for given quarter and year.
    """
    working_days = 0
    start_month = (quarter - 1) * 3 + 1
    start_date = date(year, start_month, 1)
    if quarter == 4:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, start_month + 3, 1)

    day_count = (end_date - start_date).days
    for day in (start_date + timedelta(days=i) for i in range(day_count)):
        if day.weekday() < 5:
            working_days += 1
    return working_days


def date_in_quarter(date, year, quarter):
    """
    Checks if given date belongs to given quarter of given year.
    """
    return date.month // 4 + 1 == quarter and date.year == year
