"""Tests for neotoma2faire.neo_connect."""

from unittest.mock import MagicMock, patch

import pytest


class TestNeoConnect:
    def test_uses_dbauth_test_when_tank_true(self):
        fake_creds = '{"host": "localhost", "dbname": "testdb"}'
        mock_conn = MagicMock()

        with patch('neotoma2faire.neo_connect.dotenv_values',
                   return_value={'DBAUTH_TEST': fake_creds, 'DBAUTH': '{}'}), \
             patch('neotoma2faire.neo_connect.psycopg.connect',
                   return_value=mock_conn) as mock_connect:
            from neotoma2faire.neo_connect import neo_connect
            result = neo_connect(tank=True)

        mock_connect.assert_called_once()
        kwargs = mock_connect.call_args.kwargs
        assert kwargs['host'] == 'localhost'
        assert kwargs['dbname'] == 'testdb'
        assert result is mock_conn

    def test_uses_dbauth_when_tank_false(self):
        fake_creds = '{"host": "prod-host", "dbname": "proddb"}'
        mock_conn = MagicMock()

        with patch('neotoma2faire.neo_connect.dotenv_values',
                   return_value={'DBAUTH_TEST': '{}', 'DBAUTH': fake_creds}), \
             patch('neotoma2faire.neo_connect.psycopg.connect',
                   return_value=mock_conn) as mock_connect:
            from neotoma2faire.neo_connect import neo_connect
            result = neo_connect(tank=False)

        kwargs = mock_connect.call_args.kwargs
        assert kwargs['host'] == 'prod-host'
        assert kwargs['dbname'] == 'proddb'

    def test_connect_timeout_is_five_seconds(self):
        with patch('neotoma2faire.neo_connect.dotenv_values',
                   return_value={'DBAUTH_TEST': '{}', 'DBAUTH': '{}'}), \
             patch('neotoma2faire.neo_connect.psycopg.connect',
                   return_value=MagicMock()) as mock_connect:
            from neotoma2faire.neo_connect import neo_connect
            neo_connect(tank=True)

        kwargs = mock_connect.call_args.kwargs
        assert kwargs['connect_timeout'] == 5

    def test_returns_connection(self):
        mock_conn = MagicMock()
        with patch('neotoma2faire.neo_connect.dotenv_values',
                   return_value={'DBAUTH_TEST': '{}', 'DBAUTH': '{}'}), \
             patch('neotoma2faire.neo_connect.psycopg.connect',
                   return_value=mock_conn):
            from neotoma2faire.neo_connect import neo_connect
            assert neo_connect() is mock_conn
