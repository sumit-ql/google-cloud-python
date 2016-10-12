# Copyright 2015 Google Inc.
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


class TestPage(unittest.TestCase):

    def _getTargetClass(self):
        from google.cloud.iterator import Page
        return Page

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_constructor(self):
        parent = object()
        page = self._makeOne(parent)
        self.assertIs(page._parent, parent)
        self.assertEqual(page._num_items, 0)
        self.assertEqual(page._remaining, 0)

    def test_num_items_property(self):
        page = self._makeOne(None)
        num_items = 42
        page._num_items = num_items
        self.assertEqual(page.num_items, num_items)

    def test_remaining_property(self):
        page = self._makeOne(None)
        remaining = 1337
        page._remaining = remaining
        self.assertEqual(page.remaining, remaining)

    def test___iter__(self):
        page = self._makeOne(None)
        self.assertIs(iter(page), page)

    def test__next_item_virtual(self):
        page = self._makeOne(None)
        with self.assertRaises(NotImplementedError):
            page._next_item()

    def test_iterator_calls__next_item(self):
        import six

        klass = self._getTargetClass()

        class CountItPage(klass):

            calls = 0
            values = None

            def _next_item(self):
                self.calls += 1
                return self.values.pop(0)

        page = CountItPage(None)
        page.values = [10, 11, 12]

        self.assertEqual(page.calls, 0)
        self.assertEqual(six.next(page), 10)
        self.assertEqual(page.calls, 1)
        self.assertEqual(six.next(page), 11)
        self.assertEqual(page.calls, 2)
        self.assertEqual(six.next(page), 12)
        self.assertEqual(page.calls, 3)


class TestIterator(unittest.TestCase):

    def _getTargetClass(self):
        from google.cloud.iterator import Iterator
        return Iterator

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        iterator = self._makeOne(client, PATH)
        self.assertIs(iterator.client, client)
        self.assertEqual(iterator.path, PATH)
        self.assertEqual(iterator.page_number, 0)
        self.assertIsNone(iterator.next_page_token)

    def test_constructor_w_extra_param_collision(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        extra_params = {'pageToken': 'val'}
        self.assertRaises(ValueError, self._makeOne, client, PATH,
                          extra_params=extra_params)

    def test___iter__(self):
        iterator = self._makeOne(None, None)
        self.assertIs(iter(iterator), iterator)

    def test_iterate(self):
        import six

        PATH = '/foo'
        KEY1 = 'key1'
        KEY2 = 'key2'
        ITEM1, ITEM2 = object(), object()
        ITEMS = {KEY1: ITEM1, KEY2: ITEM2}

        def _get_items(response):
            return [ITEMS[item['name']]
                    for item in response.get('items', [])]

        connection = _Connection(
            {'items': [{'name': KEY1}, {'name': KEY2}]})
        client = _Client(connection)
        iterator = self._makeOne(client, PATH)
        iterator.get_items_from_response = _get_items
        self.assertEqual(iterator.num_results, 0)

        val1 = six.next(iterator)
        self.assertEqual(val1, ITEM1)
        self.assertEqual(iterator.num_results, 1)

        val2 = six.next(iterator)
        self.assertEqual(val2, ITEM2)
        self.assertEqual(iterator.num_results, 2)

        with self.assertRaises(StopIteration):
            six.next(iterator)

        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], PATH)
        self.assertEqual(kw['query_params'], {})

    def test_has_next_page_new(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        iterator = self._makeOne(client, PATH)
        self.assertTrue(iterator.has_next_page())

    def test_has_next_page_w_number_no_token(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        iterator = self._makeOne(client, PATH)
        iterator.page_number = 1
        self.assertFalse(iterator.has_next_page())

    def test_has_next_page_w_number_w_token(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        TOKEN = 'token'
        iterator = self._makeOne(client, PATH)
        iterator.page_number = 1
        iterator.next_page_token = TOKEN
        self.assertTrue(iterator.has_next_page())

    def test_has_next_page_w_max_results_not_done(self):
        iterator = self._makeOne(None, None, max_results=3,
                                 page_token='definitely-not-none')
        iterator.page_number = 1
        self.assertLess(iterator.num_results, iterator.max_results)
        self.assertTrue(iterator.has_next_page())

    def test_has_next_page_w_max_results_done(self):
        iterator = self._makeOne(None, None, max_results=3)
        iterator.page_number = 1
        iterator.num_results = iterator.max_results
        self.assertFalse(iterator.has_next_page())

    def test_get_query_params_no_token(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        iterator = self._makeOne(client, PATH)
        self.assertEqual(iterator.get_query_params(), {})

    def test_get_query_params_w_token(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        TOKEN = 'token'
        iterator = self._makeOne(client, PATH)
        iterator.next_page_token = TOKEN
        self.assertEqual(iterator.get_query_params(),
                         {'pageToken': TOKEN})

    def test_get_query_params_w_max_results(self):
        connection = _Connection()
        client = _Client(connection)
        path = '/foo'
        max_results = 3
        iterator = self._makeOne(client, path,
                                 max_results=max_results)
        iterator.num_results = 1
        local_max = max_results - iterator.num_results
        self.assertEqual(iterator.get_query_params(),
                         {'maxResults': local_max})

    def test_get_query_params_extra_params(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        extra_params = {'key': 'val'}
        iterator = self._makeOne(client, PATH, extra_params=extra_params)
        self.assertEqual(iterator.get_query_params(), extra_params)

    def test_get_query_params_w_token_and_extra_params(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        TOKEN = 'token'
        extra_params = {'key': 'val'}
        iterator = self._makeOne(client, PATH, extra_params=extra_params)
        iterator.next_page_token = TOKEN

        expected_query = extra_params.copy()
        expected_query.update({'pageToken': TOKEN})
        self.assertEqual(iterator.get_query_params(), expected_query)

    def test_get_next_page_response_new_no_token_in_response(self):
        PATH = '/foo'
        TOKEN = 'token'
        KEY1 = 'key1'
        KEY2 = 'key2'
        connection = _Connection({'items': [{'name': KEY1}, {'name': KEY2}],
                                  'nextPageToken': TOKEN})
        client = _Client(connection)
        iterator = self._makeOne(client, PATH)
        response = iterator.get_next_page_response()
        self.assertEqual(response['items'], [{'name': KEY1}, {'name': KEY2}])
        self.assertEqual(iterator.page_number, 1)
        self.assertEqual(iterator.next_page_token, TOKEN)
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], PATH)
        self.assertEqual(kw['query_params'], {})

    def test_get_next_page_response_no_token(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        iterator = self._makeOne(client, PATH)
        iterator.page_number = 1
        self.assertRaises(RuntimeError, iterator.get_next_page_response)

    def test_reset(self):
        connection = _Connection()
        client = _Client(connection)
        PATH = '/foo'
        TOKEN = 'token'
        iterator = self._makeOne(client, PATH)
        iterator.page_number = 1
        iterator.next_page_token = TOKEN
        iterator.reset()
        self.assertEqual(iterator.page_number, 0)
        self.assertIsNone(iterator.next_page_token)

    def test_get_items_from_response_raises_NotImplementedError(self):
        PATH = '/foo'
        connection = _Connection()
        client = _Client(connection)
        iterator = self._makeOne(client, PATH)
        self.assertRaises(NotImplementedError,
                          iterator.get_items_from_response, object())


class TestMethodIterator(unittest.TestCase):

    def _getTargetClass(self):
        from google.cloud.iterator import MethodIterator
        return MethodIterator

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        wlm = _WithListMethod()
        iterator = self._makeOne(wlm.list_foo)
        self.assertEqual(iterator._method, wlm.list_foo)
        self.assertIsNone(iterator._token)
        self.assertIsNone(iterator._page_size)
        self.assertEqual(iterator._kw, {})
        self.assertIsNone(iterator._max_calls)
        self.assertEqual(iterator._page_num, 0)

    def test_ctor_explicit(self):
        wlm = _WithListMethod()
        TOKEN = wlm._letters
        SIZE = 4
        CALLS = 2
        iterator = self._makeOne(wlm.list_foo, TOKEN, SIZE, CALLS,
                                 foo_type='Bar')
        self.assertEqual(iterator._method, wlm.list_foo)
        self.assertEqual(iterator._token, TOKEN)
        self.assertEqual(iterator._page_size, SIZE)
        self.assertEqual(iterator._kw, {'foo_type': 'Bar'})
        self.assertEqual(iterator._max_calls, CALLS)
        self.assertEqual(iterator._page_num, 0)

    def test___iter___defaults(self):
        import string
        wlm = _WithListMethod()
        iterator = self._makeOne(wlm.list_foo)
        found = []
        for char in iterator:
            found.append(char)
        self.assertEqual(found, list(string.printable))
        self.assertEqual(len(wlm._called_with), len(found) // 10)
        for i, (token, size, kw) in enumerate(wlm._called_with):
            if i == 0:
                self.assertIsNone(token)
            else:
                self.assertEqual(token, string.printable[i * 10:])
            self.assertIsNone(size)
            self.assertEqual(kw, {})

    def test___iter___explicit_size_and_maxcalls_and_kw(self):
        import string
        wlm = _WithListMethod()
        iterator = self._makeOne(wlm.list_foo, page_size=2, max_calls=3,
                                 foo_type='Bar')
        found = []
        for char in iterator:
            found.append(char)
        self.assertEqual(found, list(string.printable[:2 * 3]))
        self.assertEqual(len(wlm._called_with), len(found) // 2)
        for i, (token, size, kw) in enumerate(wlm._called_with):
            if i == 0:
                self.assertIsNone(token)
            else:
                self.assertEqual(token, string.printable[i * 2:])
            self.assertEqual(size, 2)
            self.assertEqual(kw, {'foo_type': 'Bar'})


class _WithListMethod(object):

    def __init__(self):
        import string
        self._called_with = []
        self._letters = string.printable

    def list_foo(self, page_token, page_size, **kw):
        if page_token is not None:
            assert page_token == self._letters
        self._called_with.append((page_token, page_size, kw))
        if page_size is None:
            page_size = 10
        page, self._letters = (
            self._letters[:page_size], self._letters[page_size:])
        token = self._letters or None
        return page, token


class _Connection(object):

    def __init__(self, *responses):
        self._responses = responses
        self._requested = []

    def api_request(self, **kw):
        self._requested.append(kw)
        response, self._responses = self._responses[0], self._responses[1:]
        return response


class _Client(object):

    def __init__(self, connection):
        self.connection = connection
