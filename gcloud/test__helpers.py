# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest2


class Test__LocalStack(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud._helpers import _LocalStack

        return _LocalStack

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        batch1, batch2 = object(), object()
        batches = self._makeOne()
        self.assertEqual(list(batches), [])
        self.assertTrue(batches.top is None)
        batches.push(batch1)
        self.assertTrue(batches.top is batch1)
        batches.push(batch2)
        self.assertTrue(batches.top is batch2)
        popped = batches.pop()
        self.assertTrue(popped is batch2)
        self.assertTrue(batches.top is batch1)
        self.assertEqual(list(batches), [batch1])
        popped = batches.pop()
        self.assertTrue(batches.top is None)
        self.assertEqual(list(batches), [])


class Test__UTC(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud._helpers import _UTC
        return _UTC

    def _makeOne(self):
        return self._getTargetClass()()

    def test_module_property(self):
        from gcloud import _helpers as MUT

        klass = self._getTargetClass()
        self.assertTrue(isinstance(MUT.UTC, klass))

    def test_dst(self):
        import datetime

        tz = self._makeOne()
        self.assertEqual(tz.dst(None), datetime.timedelta(0))

    def test_fromutc(self):
        import datetime

        naive_epoch = datetime.datetime.utcfromtimestamp(0)
        self.assertEqual(naive_epoch.tzinfo, None)
        tz = self._makeOne()
        epoch = tz.fromutc(naive_epoch)
        self.assertEqual(epoch.tzinfo, tz)

    def test_tzname(self):
        tz = self._makeOne()
        self.assertEqual(tz.tzname(None), 'UTC')

    def test_utcoffset(self):
        import datetime

        tz = self._makeOne()
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(0))

    def test___repr__(self):
        tz = self._makeOne()
        self.assertEqual(repr(tz), '<UTC>')

    def test___str__(self):
        tz = self._makeOne()
        self.assertEqual(str(tz), 'UTC')


class Test__ensure_tuple_or_list(unittest2.TestCase):

    def _callFUT(self, arg_name, tuple_or_list):
        from gcloud._helpers import _ensure_tuple_or_list
        return _ensure_tuple_or_list(arg_name, tuple_or_list)

    def test_valid_tuple(self):
        valid_tuple_or_list = ('a', 'b', 'c', 'd')
        result = self._callFUT('ARGNAME', valid_tuple_or_list)
        self.assertEqual(result, ['a', 'b', 'c', 'd'])

    def test_valid_list(self):
        valid_tuple_or_list = ['a', 'b', 'c', 'd']
        result = self._callFUT('ARGNAME', valid_tuple_or_list)
        self.assertEqual(result, valid_tuple_or_list)

    def test_invalid(self):
        invalid_tuple_or_list = object()
        with self.assertRaises(TypeError):
            self._callFUT('ARGNAME', invalid_tuple_or_list)

    def test_invalid_iterable(self):
        invalid_tuple_or_list = 'FOO'
        with self.assertRaises(TypeError):
            self._callFUT('ARGNAME', invalid_tuple_or_list)


class Test__app_engine_id(unittest2.TestCase):

    def _callFUT(self):
        from gcloud._helpers import _app_engine_id
        return _app_engine_id()

    def test_no_value(self):
        from gcloud._testing import _Monkey
        from gcloud import _helpers

        with _Monkey(_helpers, app_identity=None):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)

    def test_value_set(self):
        from gcloud._testing import _Monkey
        from gcloud import _helpers

        APP_ENGINE_ID = object()
        APP_IDENTITY = _AppIdentity(APP_ENGINE_ID)
        with _Monkey(_helpers, app_identity=APP_IDENTITY):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, APP_ENGINE_ID)


class Test__compute_engine_id(unittest2.TestCase):

    def _callFUT(self):
        from gcloud._helpers import _compute_engine_id
        return _compute_engine_id()

    def _monkeyConnection(self, connection):
        from gcloud._testing import _Monkey
        from gcloud import _helpers

        def _factory(host, timeout):
            connection.host = host
            connection.timeout = timeout
            return connection

        return _Monkey(_helpers, HTTPConnection=_factory)

    def test_bad_status(self):
        connection = _HTTPConnection(404, None)
        with self._monkeyConnection(connection):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)

    def test_success(self):
        COMPUTE_ENGINE_ID = object()
        connection = _HTTPConnection(200, COMPUTE_ENGINE_ID)
        with self._monkeyConnection(connection):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, COMPUTE_ENGINE_ID)

    def test_socket_raises(self):
        connection = _TimeoutHTTPConnection()
        with self._monkeyConnection(connection):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)


class Test__get_production_project(unittest2.TestCase):

    def _callFUT(self):
        from gcloud._helpers import _get_production_project
        return _get_production_project()

    def test_no_value(self):
        import os
        from gcloud._testing import _Monkey

        environ = {}
        with _Monkey(os, getenv=environ.get):
            project = self._callFUT()
            self.assertEqual(project, None)

    def test_value_set(self):
        import os
        from gcloud._testing import _Monkey
        from gcloud._helpers import PROJECT

        MOCK_PROJECT = object()
        environ = {PROJECT: MOCK_PROJECT}
        with _Monkey(os, getenv=environ.get):
            project = self._callFUT()
            self.assertEqual(project, MOCK_PROJECT)


class Test__determine_default_project(unittest2.TestCase):

    def _callFUT(self, project=None):
        from gcloud._helpers import _determine_default_project
        return _determine_default_project(project=project)

    def _determine_default_helper(self, prod=None, gae=None, gce=None,
                                  project=None):
        from gcloud._testing import _Monkey
        from gcloud import _helpers

        _callers = []

        def prod_mock():
            _callers.append('prod_mock')
            return prod

        def gae_mock():
            _callers.append('gae_mock')
            return gae

        def gce_mock():
            _callers.append('gce_mock')
            return gce

        patched_methods = {
            '_get_production_project': prod_mock,
            '_app_engine_id': gae_mock,
            '_compute_engine_id': gce_mock,
        }

        with _Monkey(_helpers, **patched_methods):
            returned_project = self._callFUT(project)

        return returned_project, _callers

    def test_no_value(self):
        project, callers = self._determine_default_helper()
        self.assertEqual(project, None)
        self.assertEqual(callers, ['prod_mock', 'gae_mock', 'gce_mock'])

    def test_explicit(self):
        PROJECT = object()
        project, callers = self._determine_default_helper(project=PROJECT)
        self.assertEqual(project, PROJECT)
        self.assertEqual(callers, [])

    def test_prod(self):
        PROJECT = object()
        project, callers = self._determine_default_helper(prod=PROJECT)
        self.assertEqual(project, PROJECT)
        self.assertEqual(callers, ['prod_mock'])

    def test_gae(self):
        PROJECT = object()
        project, callers = self._determine_default_helper(gae=PROJECT)
        self.assertEqual(project, PROJECT)
        self.assertEqual(callers, ['prod_mock', 'gae_mock'])

    def test_gce(self):
        PROJECT = object()
        project, callers = self._determine_default_helper(gce=PROJECT)
        self.assertEqual(project, PROJECT)
        self.assertEqual(callers, ['prod_mock', 'gae_mock', 'gce_mock'])


class Test__millis(unittest2.TestCase):

    def _callFUT(self, value):
        from gcloud._helpers import _millis
        return _millis(value)

    def test_one_second_from_epoch(self):
        import datetime
        from gcloud._helpers import UTC

        WHEN = datetime.datetime(1970, 1, 1, 0, 0, 1, tzinfo=UTC)
        self.assertEqual(self._callFUT(WHEN), 1000)


class Test__microseconds_from_datetime(unittest2.TestCase):

    def _callFUT(self, value):
        from gcloud._helpers import _microseconds_from_datetime
        return _microseconds_from_datetime(value)

    def test_it(self):
        import datetime

        microseconds = 314159
        timestamp = datetime.datetime(1970, 1, 1, hour=0,
                                      minute=0, second=0,
                                      microsecond=microseconds)
        result = self._callFUT(timestamp)
        self.assertEqual(result, microseconds)


class Test__millis_from_datetime(unittest2.TestCase):

    def _callFUT(self, value):
        from gcloud._helpers import _millis_from_datetime
        return _millis_from_datetime(value)

    def test_w_none(self):
        self.assertTrue(self._callFUT(None) is None)

    def test_w_utc_datetime(self):
        import datetime
        import six
        from gcloud._helpers import UTC
        from gcloud._helpers import _microseconds_from_datetime

        NOW = datetime.datetime.utcnow().replace(tzinfo=UTC)
        NOW_MICROS = _microseconds_from_datetime(NOW)
        MILLIS = NOW_MICROS // 1000
        result = self._callFUT(NOW)
        self.assertTrue(isinstance(result, six.integer_types))
        self.assertEqual(result, MILLIS)

    def test_w_non_utc_datetime(self):
        import datetime
        import six
        from gcloud._helpers import _UTC
        from gcloud._helpers import _microseconds_from_datetime

        class CET(_UTC):
            _tzname = 'CET'
            _utcoffset = datetime.timedelta(hours=-1)

        zone = CET()
        NOW = datetime.datetime(2015, 7, 28, 16, 34, 47, tzinfo=zone)
        NOW_MICROS = _microseconds_from_datetime(NOW)
        MILLIS = NOW_MICROS // 1000
        result = self._callFUT(NOW)
        self.assertTrue(isinstance(result, six.integer_types))
        self.assertEqual(result, MILLIS)

    def test_w_naive_datetime(self):
        import datetime
        import six
        from gcloud._helpers import UTC
        from gcloud._helpers import _microseconds_from_datetime

        NOW = datetime.datetime.utcnow()
        UTC_NOW = NOW.replace(tzinfo=UTC)
        UTC_NOW_MICROS = _microseconds_from_datetime(UTC_NOW)
        MILLIS = UTC_NOW_MICROS // 1000
        result = self._callFUT(NOW)
        self.assertTrue(isinstance(result, six.integer_types))
        self.assertEqual(result, MILLIS)


class Test__datetime_from_microseconds(unittest2.TestCase):

    def _callFUT(self, value):
        from gcloud._helpers import _datetime_from_microseconds
        return _datetime_from_microseconds(value)

    def test_it(self):
        import datetime
        from gcloud._helpers import UTC
        from gcloud._helpers import _microseconds_from_datetime

        NOW = datetime.datetime(2015, 7, 29, 17, 45, 21, 123456,
                                tzinfo=UTC)
        NOW_MICROS = _microseconds_from_datetime(NOW)
        self.assertEqual(self._callFUT(NOW_MICROS), NOW)


class Test__total_seconds_backport(unittest2.TestCase):

    def _callFUT(self, *args, **kwargs):
        from gcloud._helpers import _total_seconds_backport
        return _total_seconds_backport(*args, **kwargs)

    def test_it(self):
        import datetime
        offset = datetime.timedelta(seconds=3,
                                    microseconds=140000)
        result = self._callFUT(offset)
        self.assertEqual(result, 3.14)


class Test__total_seconds(unittest2.TestCase):

    def _callFUT(self, *args, **kwargs):
        from gcloud._helpers import _total_seconds
        return _total_seconds(*args, **kwargs)

    def test_it(self):
        import datetime
        offset = datetime.timedelta(seconds=1,
                                    microseconds=414000)
        result = self._callFUT(offset)
        self.assertEqual(result, 1.414)


class Test__rfc3339_to_datetime(unittest2.TestCase):

    def _callFUT(self, dt_str):
        from gcloud._helpers import _rfc3339_to_datetime
        return _rfc3339_to_datetime(dt_str)

    def test_it(self):
        import datetime
        from gcloud._helpers import UTC

        year = 2009
        month = 12
        day = 17
        hour = 12
        minute = 44
        seconds = 32
        micros = 123456

        dt_str = '%d-%02d-%02dT%02d:%02d:%02d.%06dZ' % (
            year, month, day, hour, minute, seconds, micros)
        result = self._callFUT(dt_str)
        expected_result = datetime.datetime(
            year, month, day, hour, minute, seconds, micros, UTC)
        self.assertEqual(result, expected_result)


class Test__datetime_to_rfc3339(unittest2.TestCase):

    def _callFUT(self, value):
        from gcloud._helpers import _datetime_to_rfc3339
        return _datetime_to_rfc3339(value)

    def test_it(self):
        import datetime
        from gcloud._helpers import UTC

        year = 2009
        month = 12
        day = 17
        hour = 12
        minute = 44
        seconds = 32
        micros = 123456

        to_convert = datetime.datetime(
            year, month, day, hour, minute, seconds, micros, UTC)
        dt_str = '%d-%02d-%02dT%02d:%02d:%02d.%06dZ' % (
            year, month, day, hour, minute, seconds, micros)
        result = self._callFUT(to_convert)
        self.assertEqual(result, dt_str)


class Test__to_bytes(unittest2.TestCase):

    def _callFUT(self, *args, **kwargs):
        from gcloud._helpers import _to_bytes
        return _to_bytes(*args, **kwargs)

    def test_with_bytes(self):
        value = b'bytes-val'
        self.assertEqual(self._callFUT(value), value)

    def test_with_unicode(self):
        value = u'string-val'
        encoded_value = b'string-val'
        self.assertEqual(self._callFUT(value), encoded_value)

    def test_unicode_non_ascii(self):
        value = u'\u2013'  # Long hyphen
        encoded_value = b'\xe2\x80\x93'
        self.assertRaises(UnicodeEncodeError, self._callFUT, value)
        self.assertEqual(self._callFUT(value, encoding='utf-8'),
                         encoded_value)

    def test_with_nonstring_type(self):
        value = object()
        self.assertRaises(TypeError, self._callFUT, value)


class Test__pb_timestamp_to_datetime(unittest2.TestCase):

    def _callFUT(self, timestamp):
        from gcloud._helpers import _pb_timestamp_to_datetime
        return _pb_timestamp_to_datetime(timestamp)

    def test_it(self):
        import datetime
        from google.protobuf.timestamp_pb2 import Timestamp
        from gcloud._helpers import UTC

        # Epoch is midnight on January 1, 1970 ...
        dt_stamp = datetime.datetime(1970, month=1, day=1, hour=0,
                                     minute=1, second=1, microsecond=1234,
                                     tzinfo=UTC)
        # ... so 1 minute and 1 second after is 61 seconds and 1234
        # microseconds is 1234000 nanoseconds.
        timestamp = Timestamp(seconds=61, nanos=1234000)
        self.assertEqual(self._callFUT(timestamp), dt_stamp)


class Test__datetime_to_pb_timestamp(unittest2.TestCase):

    def _callFUT(self, when):
        from gcloud._helpers import _datetime_to_pb_timestamp
        return _datetime_to_pb_timestamp(when)

    def test_it(self):
        import datetime
        from google.protobuf.timestamp_pb2 import Timestamp
        from gcloud._helpers import UTC

        # Epoch is midnight on January 1, 1970 ...
        dt_stamp = datetime.datetime(1970, month=1, day=1, hour=0,
                                     minute=1, second=1, microsecond=1234,
                                     tzinfo=UTC)
        # ... so 1 minute and 1 second after is 61 seconds and 1234
        # microseconds is 1234000 nanoseconds.
        timestamp = Timestamp(seconds=61, nanos=1234000)
        self.assertEqual(self._callFUT(dt_stamp), timestamp)


class _AppIdentity(object):

    def __init__(self, app_id):
        self.app_id = app_id

    def get_application_id(self):
        return self.app_id


class _HTTPResponse(object):

    def __init__(self, status, data):
        self.status = status
        self.data = data

    def read(self):
        return self.data


class _BaseHTTPConnection(object):

    host = timeout = None

    def __init__(self):
        self._close_count = 0
        self._called_args = []
        self._called_kwargs = []

    def request(self, method, uri, **kwargs):
        self._called_args.append((method, uri))
        self._called_kwargs.append(kwargs)

    def close(self):
        self._close_count += 1


class _HTTPConnection(_BaseHTTPConnection):

    def __init__(self, status, project):
        super(_HTTPConnection, self).__init__()
        self.status = status
        self.project = project

    def getresponse(self):
        return _HTTPResponse(self.status, self.project)


class _TimeoutHTTPConnection(_BaseHTTPConnection):

    def getresponse(self):
        import socket
        raise socket.timeout('timed out')
