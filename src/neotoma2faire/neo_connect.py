import psycopg
from dotenv import dotenv_values
from json import loads
from psycopg.rows import dict_row


def neo_connect(tank: bool = True) -> psycopg.Connection:
    """_Connect to the Neotoma Database_

    Args:
        tank (bool): _Are we connecting to the Neotoma Holding Tank or the Production database?_

    Returns:
        psycopg.Connection: _A valid connection to the Neotoma Database server_
    """
    secrets = dotenv_values()
    if tank:
        CONN_STRING = loads(secrets["DBAUTH_TEST"])
    else:
        CONN_STRING = loads(secrets["DBAUTH"])
    con = psycopg.connect(**CONN_STRING, connect_timeout=5, row_factory=dict_row)
    return con
