# Copyright 2016 Google Inc.
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

import unittest


class TestClient(unittest.TestCase):

    PROJECT = 'PROJECT'
    LOGGER_NAME = 'LOGGER_NAME'
    SINK_NAME = 'SINK_NAME'
    FILTER = 'logName:syslog AND severity>=ERROR'
    DESTINATION_URI = 'faux.googleapis.com/destination'
    METRIC_NAME = 'metric_name'
    FILTER = 'logName:syslog AND severity>=ERROR'
    DESCRIPTION = 'DESCRIPTION'

    def _getTargetClass(self):
        from google.cloud.logging.client import Client
        return Client

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)
        self.assertEqual(client.project, self.PROJECT)

    def test_logging_api_wo_gax(self):
        from google.cloud._testing import _Monkey
        from google.cloud.logging import client as MUT
        from google.cloud.logging.connection import _LoggingAPI

        with _Monkey(MUT, _USE_GAX=False):
            client = self._makeOne(self.PROJECT, credentials=_Credentials())
        conn = client.connection = object()
        api = client.logging_api

        self.assertIsInstance(api, _LoggingAPI)
        self.assertIs(api._connection, conn)
        # API instance is cached
        again = client.logging_api
        self.assertIs(again, api)

    def test_logging_api_w_gax(self):
        from google.cloud.logging import client as MUT
        from google.cloud._testing import _Monkey

        wrapped = object()
        _called_with = []

        def _generated_api(*args, **kw):
            _called_with.append((args, kw))
            return wrapped

        class _GaxLoggingAPI(object):

            def __init__(self, _wrapped, client):
                self._wrapped = _wrapped
                self.client = client

        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)

        with _Monkey(MUT,
                     _USE_GAX=True,
                     GeneratedLoggingAPI=_generated_api,
                     GAXLoggingAPI=_GaxLoggingAPI):
            api = client.logging_api

        self.assertIsInstance(api, _GaxLoggingAPI)
        self.assertIs(api._wrapped, wrapped)
        self.assertIs(api.client, client)
        # API instance is cached
        again = client.logging_api
        self.assertIs(again, api)

    def test_no_gax_ctor(self):
        from google.cloud._testing import _Monkey
        from google.cloud.logging import client as MUT
        from google.cloud.logging.connection import _LoggingAPI

        creds = _Credentials()
        with _Monkey(MUT, _USE_GAX=True):
            client = self._makeOne(project=self.PROJECT, credentials=creds,
                                   use_gax=False)

        api = client.logging_api
        self.assertIsInstance(api, _LoggingAPI)

    def test_sinks_api_wo_gax(self):
        from google.cloud.logging.connection import _SinksAPI
        from google.cloud.logging import client as MUT
        from google.cloud._testing import _Monkey

        with _Monkey(MUT, _USE_GAX=False):
            client = self._makeOne(self.PROJECT, credentials=_Credentials())

        conn = client.connection = object()
        api = client.sinks_api

        self.assertIsInstance(api, _SinksAPI)
        self.assertIs(api._connection, conn)
        # API instance is cached
        again = client.sinks_api
        self.assertIs(again, api)

    def test_sinks_api_w_gax(self):
        from google.cloud.logging import client as MUT
        from google.cloud._testing import _Monkey

        wrapped = object()
        _called_with = []

        def _generated_api(*args, **kw):
            _called_with.append((args, kw))
            return wrapped

        class _GaxSinksAPI(object):

            def __init__(self, _wrapped, client):
                self._wrapped = _wrapped
                self.client = client

        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)

        with _Monkey(MUT,
                     _USE_GAX=True,
                     GeneratedSinksAPI=_generated_api,
                     GAXSinksAPI=_GaxSinksAPI):
            api = client.sinks_api

        self.assertIsInstance(api, _GaxSinksAPI)
        self.assertIs(api._wrapped, wrapped)
        self.assertIs(api.client, client)
        # API instance is cached
        again = client.sinks_api
        self.assertIs(again, api)

    def test_metrics_api_wo_gax(self):
        from google.cloud.logging.connection import _MetricsAPI
        from google.cloud.logging import client as MUT
        from google.cloud._testing import _Monkey

        with _Monkey(MUT, _USE_GAX=False):
            client = self._makeOne(self.PROJECT, credentials=_Credentials())

        conn = client.connection = object()
        api = client.metrics_api

        self.assertIsInstance(api, _MetricsAPI)
        self.assertIs(api._connection, conn)
        # API instance is cached
        again = client.metrics_api
        self.assertIs(again, api)

    def test_metrics_api_w_gax(self):
        from google.cloud.logging import client as MUT
        from google.cloud._testing import _Monkey

        wrapped = object()
        _called_with = []

        def _generated_api(*args, **kw):
            _called_with.append((args, kw))
            return wrapped

        class _GaxMetricsAPI(object):

            def __init__(self, _wrapped, client):
                self._wrapped = _wrapped
                self.client = client

        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)

        with _Monkey(MUT,
                     _USE_GAX=True,
                     GeneratedMetricsAPI=_generated_api,
                     GAXMetricsAPI=_GaxMetricsAPI):
            api = client.metrics_api

        self.assertIsInstance(api, _GaxMetricsAPI)
        self.assertIs(api._wrapped, wrapped)
        self.assertIs(api.client, client)
        # API instance is cached
        again = client.metrics_api
        self.assertIs(again, api)

    def test_logger(self):
        from google.cloud.logging.logger import Logger
        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)
        logger = client.logger(self.LOGGER_NAME)
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, self.LOGGER_NAME)
        self.assertIs(logger.client, client)
        self.assertEqual(logger.project, self.PROJECT)

    def test_list_entries_defaults(self):
        import six
        from google.cloud.logging.entries import TextEntry

        IID = 'IID'
        TEXT = 'TEXT'
        TOKEN = 'TOKEN'
        ENTRIES = [{
            'textPayload': TEXT,
            'insertId': IID,
            'resource': {
                'type': 'global',
            },
            'logName': 'projects/%s/logs/%s' % (
                self.PROJECT, self.LOGGER_NAME),
        }]
        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds,
                               use_gax=False)
        returned = {
            'entries': ENTRIES,
            'nextPageToken': TOKEN,
        }
        client.connection = _Connection(returned)

        iterator = client.list_entries()
        page = six.next(iterator.pages)
        entries = list(page)
        token = iterator.next_page_token

        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertIsInstance(entry, TextEntry)
        self.assertEqual(entry.insert_id, IID)
        self.assertEqual(entry.payload, TEXT)
        logger = entry.logger
        self.assertEqual(logger.name, self.LOGGER_NAME)
        self.assertIs(logger.client, client)
        self.assertEqual(logger.project, self.PROJECT)
        self.assertEqual(token, TOKEN)

        called_with = client.connection._called_with
        self.assertEqual(called_with, {
            'path': '/entries:list',
            'method': 'POST',
            'data': {'projectIds': [self.PROJECT]},
        })

    def test_list_entries_explicit(self):
        from google.cloud.logging import DESCENDING
        from google.cloud.logging.entries import ProtobufEntry
        from google.cloud.logging.entries import StructEntry
        from google.cloud.logging.logger import Logger

        PROJECT1 = 'PROJECT1'
        PROJECT2 = 'PROJECT2'
        FILTER = 'logName:LOGNAME'
        IID1 = 'IID1'
        IID2 = 'IID2'
        PAYLOAD = {'message': 'MESSAGE', 'weather': 'partly cloudy'}
        PROTO_PAYLOAD = PAYLOAD.copy()
        PROTO_PAYLOAD['@type'] = 'type.googleapis.com/testing.example'
        TOKEN = 'TOKEN'
        PAGE_SIZE = 42
        ENTRIES = [{
            'jsonPayload': PAYLOAD,
            'insertId': IID1,
            'resource': {
                'type': 'global',
            },
            'logName': 'projects/%s/logs/%s' % (
                self.PROJECT, self.LOGGER_NAME),
        }, {
            'protoPayload': PROTO_PAYLOAD,
            'insertId': IID2,
            'resource': {
                'type': 'global',
            },
            'logName': 'projects/%s/logs/%s' % (
                self.PROJECT, self.LOGGER_NAME),
        }]
        client = self._makeOne(self.PROJECT, credentials=_Credentials(),
                               use_gax=False)
        returned = {'entries': ENTRIES}
        client.connection = _Connection(returned)

        iterator = client.list_entries(
            projects=[PROJECT1, PROJECT2], filter_=FILTER, order_by=DESCENDING,
            page_size=PAGE_SIZE, page_token=TOKEN)
        entries = list(iterator)
        token = iterator.next_page_token

        # First, check the token.
        self.assertIsNone(token)
        # Then check the entries.
        self.assertEqual(len(entries), 2)
        entry = entries[0]
        self.assertIsInstance(entry, StructEntry)
        self.assertEqual(entry.insert_id, IID1)
        self.assertEqual(entry.payload, PAYLOAD)
        logger = entry.logger
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, self.LOGGER_NAME)
        self.assertIs(logger.client, client)
        self.assertEqual(logger.project, self.PROJECT)

        entry = entries[1]
        self.assertIsInstance(entry, ProtobufEntry)
        self.assertEqual(entry.insert_id, IID2)
        self.assertEqual(entry.payload, PROTO_PAYLOAD)
        logger = entry.logger
        self.assertEqual(logger.name, self.LOGGER_NAME)
        self.assertIs(logger.client, client)
        self.assertEqual(logger.project, self.PROJECT)

        self.assertIs(entries[0].logger, entries[1].logger)

        called_with = client.connection._called_with
        self.assertEqual(called_with, {
            'path': '/entries:list',
            'method': 'POST',
            'data': {
                'filter': FILTER,
                'orderBy': DESCENDING,
                'pageSize': PAGE_SIZE,
                'pageToken': TOKEN,
                'projectIds': [PROJECT1, PROJECT2],
            },
        })

    def test_sink_defaults(self):
        from google.cloud.logging.sink import Sink
        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)
        sink = client.sink(self.SINK_NAME)
        self.assertIsInstance(sink, Sink)
        self.assertEqual(sink.name, self.SINK_NAME)
        self.assertIsNone(sink.filter_)
        self.assertIsNone(sink.destination)
        self.assertIs(sink.client, client)
        self.assertEqual(sink.project, self.PROJECT)

    def test_sink_explicit(self):
        from google.cloud.logging.sink import Sink
        creds = _Credentials()
        client = self._makeOne(project=self.PROJECT, credentials=creds)
        sink = client.sink(self.SINK_NAME, self.FILTER, self.DESTINATION_URI)
        self.assertIsInstance(sink, Sink)
        self.assertEqual(sink.name, self.SINK_NAME)
        self.assertEqual(sink.filter_, self.FILTER)
        self.assertEqual(sink.destination, self.DESTINATION_URI)
        self.assertIs(sink.client, client)
        self.assertEqual(sink.project, self.PROJECT)

    def test_list_sinks_no_paging(self):
        import six
        from google.cloud.logging.sink import Sink

        PROJECT = 'PROJECT'
        TOKEN = 'TOKEN'
        SINK_NAME = 'sink_name'
        FILTER = 'logName:syslog AND severity>=ERROR'
        SINKS = [{
            'name': SINK_NAME,
            'filter': FILTER,
            'destination': self.DESTINATION_URI,
        }]
        client = self._makeOne(project=PROJECT, credentials=_Credentials(),
                               use_gax=False)
        returned = {
            'sinks': SINKS,
            'nextPageToken': TOKEN,
        }
        client.connection = _Connection(returned)

        iterator = client.list_sinks()
        page = six.next(iterator.pages)
        sinks = list(page)
        token = iterator.next_page_token

        # First check the token.
        self.assertEqual(token, TOKEN)
        # Then check the sinks returned.
        self.assertEqual(len(sinks), 1)
        sink = sinks[0]
        self.assertIsInstance(sink, Sink)
        self.assertEqual(sink.name, SINK_NAME)
        self.assertEqual(sink.filter_, FILTER)
        self.assertEqual(sink.destination, self.DESTINATION_URI)
        self.assertIs(sink.client, client)

        # Verify the mocked transport.
        called_with = client.connection._called_with
        path = '/projects/%s/sinks' % (self.PROJECT,)
        self.assertEqual(called_with, {
            'method': 'GET',
            'path': path,
            'query_params': {},
        })

    def test_list_sinks_with_paging(self):
        from google.cloud.logging.sink import Sink

        PROJECT = 'PROJECT'
        SINK_NAME = 'sink_name'
        FILTER = 'logName:syslog AND severity>=ERROR'
        TOKEN = 'TOKEN'
        PAGE_SIZE = 42
        SINKS = [{
            'name': SINK_NAME,
            'filter': FILTER,
            'destination': self.DESTINATION_URI,
        }]
        client = self._makeOne(project=PROJECT, credentials=_Credentials(),
                               use_gax=False)
        returned = {
            'sinks': SINKS,
        }
        client.connection = _Connection(returned)

        iterator = client.list_sinks(PAGE_SIZE, TOKEN)
        sinks = list(iterator)
        token = iterator.next_page_token

        # First check the token.
        self.assertIsNone(token)
        # Then check the sinks returned.
        self.assertEqual(len(sinks), 1)
        sink = sinks[0]
        self.assertIsInstance(sink, Sink)
        self.assertEqual(sink.name, SINK_NAME)
        self.assertEqual(sink.filter_, FILTER)
        self.assertEqual(sink.destination, self.DESTINATION_URI)
        self.assertIs(sink.client, client)

        # Verify the mocked transport.
        called_with = client.connection._called_with
        path = '/projects/%s/sinks' % (self.PROJECT,)
        self.assertEqual(called_with, {
            'method': 'GET',
            'path': path,
            'query_params': {
                'pageSize': PAGE_SIZE,
                'pageToken': TOKEN,
            },
        })

    def test_metric_defaults(self):
        from google.cloud.logging.metric import Metric
        creds = _Credentials()

        client_obj = self._makeOne(project=self.PROJECT, credentials=creds)
        metric = client_obj.metric(self.METRIC_NAME)
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.name, self.METRIC_NAME)
        self.assertIsNone(metric.filter_)
        self.assertEqual(metric.description, '')
        self.assertIs(metric.client, client_obj)
        self.assertEqual(metric.project, self.PROJECT)

    def test_metric_explicit(self):
        from google.cloud.logging.metric import Metric
        creds = _Credentials()

        client_obj = self._makeOne(project=self.PROJECT, credentials=creds)
        metric = client_obj.metric(self.METRIC_NAME, self.FILTER,
                                   description=self.DESCRIPTION)
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.name, self.METRIC_NAME)
        self.assertEqual(metric.filter_, self.FILTER)
        self.assertEqual(metric.description, self.DESCRIPTION)
        self.assertIs(metric.client, client_obj)
        self.assertEqual(metric.project, self.PROJECT)

    def test_list_metrics_no_paging(self):
        from google.cloud.logging.metric import Metric
        PROJECT = 'PROJECT'
        TOKEN = 'TOKEN'
        METRICS = [{
            'name': self.METRIC_NAME,
            'filter': self.FILTER,
            'description': self.DESCRIPTION,
        }]
        client = self._makeOne(project=PROJECT, credentials=_Credentials())
        api = client._metrics_api = _DummyMetricsAPI()
        api._list_metrics_response = METRICS, TOKEN

        metrics, token = client.list_metrics()

        self.assertEqual(len(metrics), 1)
        metric = metrics[0]
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.name, self.METRIC_NAME)
        self.assertEqual(metric.filter_, self.FILTER)
        self.assertEqual(metric.description, self.DESCRIPTION)
        self.assertEqual(token, TOKEN)
        self.assertEqual(api._list_metrics_called_with,
                         (PROJECT, None, None))

    def test_list_metrics_with_paging(self):
        from google.cloud.logging.metric import Metric
        PROJECT = 'PROJECT'
        TOKEN = 'TOKEN'
        PAGE_SIZE = 42
        METRICS = [{
            'name': self.METRIC_NAME,
            'filter': self.FILTER,
            'description': self.DESCRIPTION,
        }]
        client = self._makeOne(project=PROJECT, credentials=_Credentials())
        api = client._metrics_api = _DummyMetricsAPI()
        api._list_metrics_response = METRICS, None

        # Execute request.
        metrics, token = client.list_metrics(PAGE_SIZE, TOKEN)
        # Test values are correct.
        self.assertEqual(len(metrics), 1)
        metric = metrics[0]
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.name, self.METRIC_NAME)
        self.assertEqual(metric.filter_, self.FILTER)
        self.assertEqual(metric.description, self.DESCRIPTION)
        self.assertIsNone(token)
        self.assertEqual(api._list_metrics_called_with,
                         (PROJECT, PAGE_SIZE, TOKEN))


class _Credentials(object):

    _scopes = None

    @staticmethod
    def create_scoped_required():
        return True

    def create_scoped(self, scope):
        self._scopes = scope
        return self


class _DummyMetricsAPI(object):

    def list_metrics(self, project, page_size, page_token):
        self._list_metrics_called_with = (project, page_size, page_token)
        return self._list_metrics_response


class _Connection(object):

    _called_with = None

    def __init__(self, *responses):
        self._responses = responses

    def api_request(self, **kw):
        self._called_with = kw
        response, self._responses = self._responses[0], self._responses[1:]
        return response
