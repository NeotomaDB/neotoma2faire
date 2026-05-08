"""Tests for neotoma2faire.utils (formatting helpers only).

The rpy2-dependent helpers (_r_to_df, _r_subset) are thin pass-throughs to
rpy2 and are covered implicitly by the get_data / get_taxa tests via mocking.
"""

import pytest
from neotoma2faire.utils import format_db_value #, apply_query_result


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
