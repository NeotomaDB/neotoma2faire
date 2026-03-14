"""Shared utility helpers used across the neotoma2faire package.

Three groups of helpers live here:

* **R / rpy2** — thin wrappers around common rpy2 conversions so that each
  module that talks to R does not duplicate the same boilerplate.
* **Excel / DB value formatting** — helpers for writing database query results
  into openpyxl worksheet cells.
"""

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri


# ---------------------------------------------------------------------------
# R / rpy2 helpers
# ---------------------------------------------------------------------------

def _r_to_df(r_obj):
    """Convert an R object to a pandas DataFrame.

    Calls ``as.data.frame`` on the R object via rpy2, then uses
    ``pandas2ri`` to produce a native pandas DataFrame.

    Args:
        r_obj: Any rpy2 R object that can be coerced with ``as.data.frame``.

    Returns:
        pandas.DataFrame: The converted DataFrame.
    """
    df = ro.r('function(x) as.data.frame(x)')(r_obj)
    return pandas2ri.rpy2py(df)


def _r_subset(r_obj, condition):
    """Subset an R object using an R expression string.

    Equivalent to calling ``subset(x, <condition>)`` in R.

    Args:
        r_obj: An rpy2 R object (typically a data frame).
        condition (str): A valid R logical expression used as the ``subset``
            argument, e.g. ``'siteid == 1766'``.

    Returns:
        An rpy2 R object containing only the rows that satisfy *condition*.
    """
    return ro.r(f'function(x) subset(x, {condition})')(r_obj)


# ---------------------------------------------------------------------------
# Excel / DB value formatting helpers
# ---------------------------------------------------------------------------

def format_db_value(v, none_placeholder=''):
    """Format a single database value for writing to a worksheet cell.

    Lists are joined with ``'; '`` after filtering out ``None`` entries.
    A bare ``None`` is replaced by *none_placeholder*.  All other values are
    returned unchanged.

    Args:
        v: The value to format.  May be a ``list``, ``None``, or a scalar.
        none_placeholder (str): String to use when *v* is ``None`` or an
            empty list.  Defaults to ``''``.

    Returns:
        str | Any: Formatted value suitable for an openpyxl cell.
    """
    if isinstance(v, list):
        filtered = [str(s) for s in v if s is not None]
        return '; '.join(filtered) if filtered else none_placeholder
    elif v is None:
        return none_placeholder
    return v


def apply_query_result(result, key_map, write_fn, none_placeholder=''):
    """Map database query results onto a worksheet using a pre-built key lookup.

    Iterates over *result* rows and, for each key that appears in *key_map*,
    calls *write_fn* so that the caller can write the value to the appropriate
    cell.

    Args:
        result: Iterable of dict-like rows returned by ``cursor.fetchall()``.
        key_map (dict): Mapping of database field name to the index that will
            be forwarded to *write_fn*.
        write_fn (callable): ``write_fn(row_idx, mapped_idx, value)`` —
            receives the 0-based row index within *result*, the mapped index
            from *key_map*, and the formatted cell value.
        none_placeholder (str): Passed to :func:`format_db_value` for
            ``None`` values.  Defaults to ``''``.
    """
    for row_idx, row in enumerate(result):
        for k, v in row.items():
            if k not in key_map:
                continue
            value = format_db_value(v, none_placeholder)
            write_fn(row_idx, key_map[k], value)
