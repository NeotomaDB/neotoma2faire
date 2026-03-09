def format_db_value(v, none_placeholder=''):

    """Format a single DB value for writing to a sheet cell."""
    if isinstance(v, list):
        filtered = [str(s) for s in v if s is not None]
        return '; '.join(filtered) if filtered else none_placeholder
    elif v is None:
        return none_placeholder
    return v


def apply_query_result(result, key_map, write_fn, none_placeholder=''):
    """Map DB query results onto a sheet using a pre-built key lookup.

    Args:
        result:           iterable of dict-like rows from cursor.fetchall()
        key_map:          dict mapping DB field name -> index passed to write_fn
        write_fn:         callable(row_idx, mapped_idx, value) — handles cell writes
        none_placeholder: string to use when a value is None
    """
    for row_idx, row in enumerate(result):
        for k, v in row.items():
            if k not in key_map:
                continue
            value = format_db_value(v, none_placeholder)
            write_fn(row_idx, key_map[k], value)
