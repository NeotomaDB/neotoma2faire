"""Database connection helper for the Neotoma PostgreSQL backend.

Reads connection credentials from a ``.env`` file via ``dotenv`` and returns
a ``psycopg`` connection configured with the ``dict_row`` row factory so that
cursor results are plain Python dicts.
"""

from json import loads

import psycopg
from dotenv import dotenv_values
from psycopg.rows import dict_row


def neo_connect(tank: bool = True) -> psycopg.Connection:
    """Open a connection to the Neotoma database.

    Reads credentials from the ``.env`` file in the current working
    directory.  Use ``DBAUTH_TEST`` for the holding-tank database and
    ``DBAUTH`` for the production database (both stored as JSON strings).

    Args:
        tank (bool): When ``True`` (default), connects to the Neotoma
            holding tank using the ``DBAUTH_TEST`` credential.  When
            ``False``, connects to the production database using ``DBAUTH``.

    Returns:
        psycopg.Connection: Open database connection with a 5-second
        connect timeout and the ``dict_row`` row factory active.
    """
    secrets = dotenv_values()
    if tank:
        CONN_STRING = loads(secrets["DBAUTH_TEST"])
    else:
        CONN_STRING = loads(secrets["DBAUTH"])
    con = psycopg.connect(**CONN_STRING, connect_timeout=5, row_factory=dict_row)
    return con
