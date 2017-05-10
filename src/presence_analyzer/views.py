# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import abort, redirect, url_for
from flask_mako import exceptions, render_template

from presence_analyzer.main import app
from presence_analyzer.utils import (
    get_data,
    get_data_xml,
    group_by_weekday,
    group_by_weekday_start_end,
    group_quarters,
    jsonify,
    mean,
    overtime_hours_in_quarter,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('render_by_name', name='presence_weekday'))


@app.route('/<string:name>')
def render_by_name(name):
    """
    Renders template that matches given name.
    """
    try:
        return render_template('{}.html'.format(name))
    except exceptions.TopLevelLookupException:
        abort(404)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data_xml()
    return [
        {
            'user_id': i,
            'name': user.get('name'),
            'avatar': user.get('avatar'),
        }
        for i, user in data.items()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean start time and mean end time for given user
    grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday_start_end(data[user_id])
    result = [
        (
            calendar.day_abbr[weekday],
            mean(time.get('start', [])),
            mean(time.get('end', [])),
        )
        for weekday, time in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/quarters', methods=['GET'])
@jsonify
def quarters_view():
    """
    Quarters listing for dropdown.
    """
    data = get_data()
    quarters = group_quarters(data)
    return sorted([
        {
            'quarter_id': i,
            'name': '{} quarter of {}'.format(
                quarter['numeral'],
                quarter['year'],
            ),
        }
        for i, quarter in quarters.items()
    ], key=lambda x: x.get('quarter_id'), reverse=True)


@app.route('/api/v1/overtime_in_quarter/<int:quarter_id>', methods=['GET'])
@jsonify
def overtime_in_quarter(quarter_id):
    """
    Returns top 3 users with most overtime hours in given quarter.
    """
    data = get_data()
    users = get_data_xml()
    quarters = group_quarters(data)
    result = overtime_hours_in_quarter(data, quarters[quarter_id])
    return sorted(
        [
            (
                users.get(user_id, {'name': 'User {}'.format(user_id)}),
                hours,
            )
            for user_id, hours in result.items() if hours > 0
        ],
        key=lambda x: x[1],
        reverse=True
    )[:3]
