# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import os.path
import json
import datetime
import unittest

from presence_analyzer import main, utils

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up an environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday')

    def test_render_by_name(self):
        """
        Test rendering template for given template name.
        """
        resp = self.client.get('/presence_weekday')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/wrong_template')
        self.assertEqual(resp.status_code, 404)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)
        user = {
            'user_id': 10,
            'name': 'John Doe',
            'avatar': 'https://intranet.stxnext.pl:1234/api/images/users/10',
        }
        self.assertDictEqual(data[0], user)

    def test_mean_time_weekday(self):
        """
        Test mean presence time for given user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Mon', 0],
                ['Tue', 30047.0],
                ['Wed', 24465.0],
                ['Thu', 23705.0],
                ['Fri', 0],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )

        resp = self.client.get('/api/v1/mean_time_weekday/11')
        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Mon', 24123.0],
                ['Tue', 16564.0],
                ['Wed', 25321.0],
                ['Thu', 22984.0],
                ['Fri', 6426.0],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )

    def test_presence_weekday(self):
        """
        Test total presence time for given user.
        """
        resp = self.client.get('/api/v1/presence_weekday/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Weekday', 'Presence (s)'],
                ['Mon', 0],
                ['Tue', 30047],
                ['Wed', 24465],
                ['Thu', 23705],
                ['Fri', 0],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )

        resp = self.client.get('/api/v1/presence_weekday/11')
        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Weekday', 'Presence (s)'],
                ['Mon', 24123],
                ['Tue', 16564],
                ['Wed', 25321],
                ['Thu', 45968],
                ['Fri', 6426],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )

    def test_presence_start_end(self):
        """
        Test mean start time and mean end time for given user.
        """
        resp = self.client.get('/api/v1/presence_start_end/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Mon', 0, 0],
                ['Tue', 34745, 64792],
                ['Wed', 33592, 58057],
                ['Thu', 38926, 62631],
                ['Fri', 0, 0],
                ['Sat', 0, 0],
                ['Sun', 0, 0],
            ]
        )

        resp = self.client.get('/api/v1/presence_start_end/11')
        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Mon', 33134, 57257],
                ['Tue', 33590, 50154],
                ['Wed', 33206, 58527],
                ['Thu', 35602, 58586],
                ['Fri', 47816, 54242],
                ['Sat', 0, 0],
                ['Sun', 0, 0],
            ]
        )

    def test_quarters(self):
        """
        Test quarters listing.
        """
        resp = self.client.get('/api/v1/quarters')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [{'quarter_id': 0, 'name': '3 quarter of 2013'}],
        )

    def test_overtime_in_quarter(self):
        """
        Test counting overtime hours in quarter.
        """
        resp = self.client.get('/api/v1/overtime_in_quarter/0')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        result = [
            [{
                'name': 'Overtime Master',
                'avatar': 'https://intranet.stxnext.pl:1234/api/images/users/15',
            }, 176],
            [{
                'name': 'User 14',
            }, 132],
            [{
                'name': 'User 25',
            }, 22],
        ]
        self.assertEqual(data, result)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up an environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11, 14, 15, 25])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_data_xml(self):
        """
        Test parsing of XML file.
        """
        data = utils.get_data_xml()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 12, 15])
        self.assertEqual(data[10]['name'], 'John Doe')

    def test_group_by_weekday(self):
        """
        Test grouping presences by weekday.
        """
        test_data = {
            datetime.date(2017, 4, 18): {
                'start': datetime.time(8, 15, 0),
                'end': datetime.time(16, 0, 0),
            },
            datetime.date(2017, 4, 19): {
                'start': datetime.time(13, 21, 30),
                'end': datetime.time(15, 4, 2),
            },
        }
        self.assertEqual(
            [[], [27900], [6152], [], [], [], []],
            utils.group_by_weekday(test_data)
        )

        # more dates for weekday 1 to test if they are counted
        test_data[datetime.date(2017, 4, 25)] = {
            'start': datetime.time(0, 0, 0),
            'end': datetime.time(0, 0, 0),
        }
        test_data[datetime.date(2017, 4, 11)] = {
            'start': datetime.time(8, 0, 0),
            'end': datetime.time(16, 0, 0),
        }
        self.assertEqual(3, len(utils.group_by_weekday(test_data)[1]))

        data = utils.get_data()
        self.assertEqual(
            [[], [30047], [24465], [23705], [], [], []],
            utils.group_by_weekday(data[10])
        )
        self.assertEqual(
            [[24123], [16564], [25321], [22969, 22999], [6426], [], []],
            utils.group_by_weekday(data[11])
        )

    def test_group_by_weekday_start_end(self):
        """
        Test grouping presences by weekday with start and end time.
        """
        data = utils.get_data()
        result = [
            {},
            {'start': [34745], 'end': [64792]},
            {'start': [33592], 'end': [58057]},
            {'start': [38926], 'end': [62631]},
            {},
            {},
            {},
        ]
        self.assertEqual(result, utils.group_by_weekday_start_end(data[10]))

        result = [
            {'start': [33134], 'end': [57257]},
            {'start': [33590], 'end': [50154]},
            {'start': [33206], 'end': [58527]},
            {'start': [37116, 34088], 'end': [60085, 57087]},
            {'start': [47816], 'end': [54242]},
            {},
            {},
        ]
        self.assertEqual(result, utils.group_by_weekday_start_end(data[11]))

    def test_seconds_since_midnight(self):
        """
        Test calculation of amount of seconds since midnight.
        """
        midnight = datetime.time(0, 0, 0)
        self.assertEqual(0, utils.seconds_since_midnight(midnight))

        simple = datetime.time(10, 0, 0)
        self.assertEqual(36000, utils.seconds_since_midnight(simple))

        time = datetime.time(12, 20, 5)
        self.assertEqual(44405, utils.seconds_since_midnight(time))

        almost = datetime.time(23, 59, 59)
        self.assertEqual(86399, utils.seconds_since_midnight(almost))

    def test_interval(self):
        """
        Test calculation of interval between start time and end time.
        """
        start = datetime.time(0, 0, 0)
        end = datetime.time(0, 0, 0)
        self.assertEqual(0, utils.interval(start, end))

        start = datetime.time(0, 20, 5)
        end = datetime.time(10, 0, 0)
        self.assertEqual(34795, utils.interval(start, end))

        start = datetime.time(0, 36, 31)
        end = datetime.time(0, 36, 32)
        self.assertEqual(1, utils.interval(start, end))

    def test_mean(self):
        """
        Test calculation of arithmetic mean.
        """
        self.assertEqual(2.0, utils.mean([1, 2, 3]))
        self.assertEqual(2.6, utils.mean([1.5, 2.5, 3.8]))
        self.assertEqual(1.0, utils.mean([0, 2]))
        self.assertEqual(0, utils.mean([]))

    def test_cache(self):
        """
        Test caching data for given time.
        """
        def func():
            """
            Returns empty list. Just for testing purposes.
            """
            return []

        utils.cache.data.clear()
        data_1 = func()
        data_2 = func()
        self.assertIsNot(data_1, data_2)

        wrapped_func = utils.cache(5)(func)
        wrapped_data_1 = wrapped_func()
        wrapped_data_2 = wrapped_func()
        self.assertIs(wrapped_data_1, wrapped_data_2)

        wrapped_func = utils.cache(0)(func)
        wrapped_data_1 = wrapped_func()
        wrapped_data_2 = wrapped_func()
        self.assertIsNot(wrapped_data_1, wrapped_data_2)
        utils.cache.data.clear()

    def test_group_quarters(self):
        """
        Test grouping quarters by year and numeral.
        """
        data = utils.get_data()
        result = {
            0: {
                'numeral': 3,
                'year': 2013,
            }
        }
        self.assertEqual(result, utils.group_quarters(data))

    def test_overtime_hours_in_quarter(self):
        """
        Test calculation of overtime hours for every user in given quarter.
        """
        data = utils.get_data()
        quarter = utils.group_quarters(data)[0]
        hours = {
            10: -507,
            11: -496,
            14: 132,
            15: 176,
            25: 22,
        }
        self.assertEqual(hours, utils.overtime_hours_in_quarter(data, quarter))

    def test_working_days_in_quarter(self):
        """
        Test calculation of working days for given quarter and year.
        """
        self.assertEqual(65, utils.working_days_in_quarter(2016, 1))
        self.assertEqual(65, utils.working_days_in_quarter(2016, 2))
        self.assertEqual(66, utils.working_days_in_quarter(2016, 3))
        self.assertEqual(65, utils.working_days_in_quarter(2016, 4))

        self.assertEqual(65, utils.working_days_in_quarter(2018, 1))
        self.assertEqual(65, utils.working_days_in_quarter(2018, 2))
        self.assertEqual(65, utils.working_days_in_quarter(2018, 3))
        self.assertEqual(66, utils.working_days_in_quarter(2018, 4))

    def test_date_in_quarter(self):
        """
        Test checking if date belongs to given quarter.
        """
        test_date = datetime.date(2013, 2, 23)
        self.assertTrue(utils.date_in_quarter(test_date, 2013, 1))
        self.assertFalse(utils.date_in_quarter(test_date, 2013, 2))
        self.assertFalse(utils.date_in_quarter(test_date, 2014, 1))

        test_date = datetime.date(2013, 4, 1)
        self.assertFalse(utils.date_in_quarter(test_date, 2013, 1))


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
