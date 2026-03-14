"""Tests for neotoma2faire.utils (formatting helpers only).

The rpy2-dependent helpers (_r_to_df, _r_subset) are thin pass-throughs to
rpy2 and are covered implicitly by the get_data / get_taxa tests via mocking.
"""

import pytest
from neotoma2faire.utils import format_db_value, apply_query_result


class TestFormatDbValue:
    def test_none_returns_empty_string_by_default(self):
        assert format_db_value(None) == ''

    def test_none_returns_custom_placeholder(self):
        assert format_db_value(None, none_placeholder='N/A') == 'N/A'

    def test_scalar_string_returned_unchanged(self):
        assert format_db_value('hello') == 'hello'

    def test_scalar_int_returned_unchanged(self):
        assert format_db_value(42) == 42

    def test_list_joined_with_semicolons(self):
        assert format_db_value(['a', 'b', 'c']) == 'a; b; c'

    def test_list_filters_none_entries(self):
        assert format_db_value(['a', None, 'c']) == 'a; c'

    def test_list_all_none_returns_placeholder(self):
        assert format_db_value([None, None], none_placeholder='empty') == 'empty'

    def test_empty_list_returns_placeholder(self):
        assert format_db_value([], none_placeholder='empty') == 'empty'

    def test_list_of_ints_joined(self):
        assert format_db_value([1, 2, 3]) == '1; 2; 3'


class TestApplyQueryResult:
    def _make_result(self):
        return [
            {'name': 'Alice', 'age': 30, 'ignored': 'x'},
            {'name': 'Bob',   'age': 25, 'ignored': 'y'},
        ]

    def test_calls_write_fn_for_mapped_keys(self):
        calls = []
        key_map = {'name': 0, 'age': 1}
        apply_query_result(self._make_result(), key_map, lambda r, k, v: calls.append((r, k, v)))
        assert (0, 0, 'Alice') in calls
        assert (0, 1, 30) in calls
        assert (1, 0, 'Bob') in calls
        assert (1, 1, 25) in calls

    def test_skips_keys_not_in_key_map(self):
        calls = []
        key_map = {'name': 0}
        apply_query_result(self._make_result(), key_map, lambda r, k, v: calls.append(k))
        # Only 'name' mapped; 'age' and 'ignored' must not appear
        assert all(k == 0 for k in calls)

    def test_none_value_uses_placeholder(self):
        result = [{'field': None}]
        key_map = {'field': 0}
        received = []
        apply_query_result(result, key_map, lambda r, k, v: received.append(v),
                           none_placeholder='MISSING')
        assert received == ['MISSING']

    def test_empty_result_no_calls(self):
        calls = []
        apply_query_result([], {'name': 0}, lambda r, k, v: calls.append(1))
        assert calls == []

    def test_list_value_joined(self):
        result = [{'tags': ['a', 'b']}]
        key_map = {'tags': 0}
        received = []
        apply_query_result(result, key_map, lambda r, k, v: received.append(v))
        assert received == ['a; b']
