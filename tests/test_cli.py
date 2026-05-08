"""Tests for neotoma2faire.cli."""

from unittest.mock import MagicMock, patch
import pytest


class TestParseArgs:
    def _parse(self, argv):
        with patch('sys.argv', ['neotoma2faire'] + argv):
            from neotoma2faire.cli import parse_args
            return parse_args()

    def test_tool_template(self):
        args = self._parse(['template'])
        assert 'template' in args.tool

    def test_custom_output(self):
        args = self._parse(['template', '-o', 'out.xlsx'])
        assert args.output == 'out.xlsx'

    def test_default_dataset(self):
        args = self._parse(['template'])
        assert args.dataset == 55582

    def test_custom_dataset(self):
        args = self._parse(['template', '-d', '12345'])
        assert args.dataset == 12345

    def test_default_template_path(self):
        args = self._parse(['template'])
        assert 'FAIRe' in args.template


class TestMain:
    def test_main_calls_make_template(self):
        mock_args = MagicMock()
        mock_args.tool = ['template']

        with patch('neotoma2faire.cli.parse_args', return_value=mock_args), \
             patch('neotoma2faire.cli.ntf.make_template') as mock_make:
            from neotoma2faire.cli import main
            main()

        mock_make.assert_called_once_with(mock_args)

    def test_main_does_not_call_make_template_for_unknown_tool(self):
        mock_args = MagicMock()
        mock_args.tool = ['unknown']

        with patch('neotoma2faire.cli.parse_args', return_value=mock_args), \
             patch('neotoma2faire.cli.ntf.make_template') as mock_make:
            from neotoma2faire.cli import main
            main()

        mock_make.assert_not_called()
