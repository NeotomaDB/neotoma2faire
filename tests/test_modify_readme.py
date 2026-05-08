"""Tests for neotoma2faire.write.readme."""

from datetime import datetime
from unittest.mock import MagicMock, call, patch

import pytest
from neotoma2faire.write.readme import modify_README


@pytest.fixture
def mock_workbook():
    """Build a minimal openpyxl-like workbook mock with a README sheet."""
    ws = MagicMock()
    wb = MagicMock()
    wb.__getitem__ = MagicMock(return_value=ws)
    return wb, ws


class TestModifyREADME:
    def test_returns_workbook(self, mock_workbook):
        wb, _ = mock_workbook
        result = modify_README(wb)
        assert result is wb

    def test_inserts_rows_at_position_3(self, mock_workbook):
        wb, ws = mock_workbook
        modify_README(wb)
        ws.insert_rows.assert_any_call(3, 2)

    def test_inserts_extra_row_at_position_6(self, mock_workbook):
        wb, ws = mock_workbook
        modify_README(wb)
        ws.insert_rows.assert_any_call(6, 1)

    def test_writes_modified_by_label(self, mock_workbook):
        wb, ws = mock_workbook
        modify_README(wb)
        assert ws.__setitem__.call_args_list[0] == call('A4', 'Modified by:')

    def test_writes_tool_version(self, mock_workbook):
        wb, ws = mock_workbook
        modify_README(wb)
        assert ws.__setitem__.call_args_list[1] == call('A5', 'neotoma2FAIRe v0.1.0')

    def test_writes_datetime_to_a8(self, mock_workbook):
        wb, ws = mock_workbook
        fixed = datetime(2026, 1, 1, 12, 0, 0)
        with patch('neotoma2faire.write.readme.datetime') as mock_dt:
            mock_dt.now.return_value = fixed
            modify_README(wb)
        assert ws.__setitem__.call_args_list[2] == call('A8', fixed)

    def test_activates_readme_sheet(self, mock_workbook):
        wb, ws = mock_workbook
        modify_README(wb)
        wb.__getitem__.assert_called_with('README')
