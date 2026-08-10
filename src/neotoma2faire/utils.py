# ---------------------------------------------------------------------------
# Excel / DB value formatting helpers
# ---------------------------------------------------------------------------

import re
from pathlib import Path

import pandas as pd


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


def write_sheet_rows(ws, df, header_row: int) -> None:
    """Write DataFrame rows into an openpyxl worksheet.

    Reads the column-name → column-index mapping from *header_row* of *ws*,
    then writes one data row per DataFrame row starting at ``header_row + 1``.
    Columns present in the sheet header but absent from *df* are skipped.
    ``NaN`` values are converted to ``None`` before writing.

    Uses ``df.to_dict(orient='records')`` internally so that column names
    containing spaces or special characters (e.g. ``'CRS (Calendar year)'``)
    are handled correctly.

    Args:
        ws: An openpyxl ``Worksheet``.
        df (pandas.DataFrame): Rows to write.
        header_row (int): 1-based row index of the column-name header in *ws*.
    """
    header = {cell.value: cell.column for cell in ws[header_row]}
    for row_idx, row_dict in enumerate(df.to_dict(orient="records"), start=header_row + 1):
        for col_name, col_idx in header.items():
            if col_name not in df.columns:
                continue
            value = row_dict.get(col_name)
            try:
                if pd.isna(value):
                    value = None
            except (TypeError, ValueError):
                pass
            try:
                ws.cell(row=row_idx, column=col_idx, value=value)
            except ValueError:
                ws.cell(row=row_idx, column=col_idx, value=None)


def write_flat_sheet(wb, sheet_name: str, df, after: str | None = None):
    """Write *df* to a sheet that carries a single header row.

    The FAIRe checklist sheets ship with a 3-row header already in the
    template, so they are written with :func:`write_sheet_rows` alone.  The
    extra sheets Neotoma exports alongside them (``ageModels``, ``finalReads``)
    are not in the checklist at all: they have to be created, and their columns
    are data-dependent, so the header is written from ``df.columns``.

    Args:
        wb (openpyxl.Workbook): Target workbook.
        sheet_name (str): Sheet to create (or reuse, if already present).
        df (pandas.DataFrame): Rows to write.  Nothing happens when empty.
        after (str | None): Name of the sheet the new one should follow.
            Ignored when that sheet is absent.  Defaults to ``None`` (append).

    Returns:
        The worksheet written, or ``None`` when *df* was empty.
    """
    if df is None or df.empty:
        return None

    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    elif after in wb.sheetnames:
        ws = wb.create_sheet(sheet_name, wb.sheetnames.index(after) + 1)
    else:
        ws = wb.create_sheet(sheet_name)

    for col_idx, col_name in enumerate(df.columns, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)
    write_sheet_rows(ws, df, header_row=1)
    return ws


def add_sheet_from_dataset(wb, sheet_name: str, getter_fn, dataset_id: int, header_row: int = 3):
    """Fetch dataset rows via *getter_fn* and write them to *sheet_name*.

    A generic helper shared by :func:`~.add_amp_data.add_amp_data`,
    :func:`~.add_std_data.add_std_data`, and
    :func:`~.add_elow_quant.add_elow_quant`.  Each of those modules calls a
    different ``get_*`` function and targets a different sheet, but the
    surrounding logic is identical:

    1. Call ``getter_fn(dataset_id)`` → DataFrame.
    2. If the DataFrame is not empty, write it to ``wb[sheet_name]``.
    3. Return the DataFrame (empty or not) for the caller's use.

    Args:
        wb (openpyxl.Workbook): Target workbook.
        sheet_name (str): Name of the worksheet to populate.
        getter_fn (callable): A ``get_*(dataset_id) -> pd.DataFrame`` function.
        dataset_id (int): Neotoma dataset ID forwarded to *getter_fn*.
        header_row (int): 1-based row index of the column-name header in the
            target sheet.  Defaults to ``3``.

    Returns:
        pandas.DataFrame: The data written to the sheet, or an empty DataFrame
        if *getter_fn* returned no rows.
    """
    df = getter_fn(dataset_id)
    if not df.empty:
        write_sheet_rows(wb[sheet_name], df, header_row)
    return df


# ---------------------------------------------------------------------------
# Sample ordering
# ---------------------------------------------------------------------------

def natural_key(name) -> tuple:
    """Sort key that orders ``WLO9`` before ``WLO10``.

    Splits *name* into runs of digits and non-digits and casts the digit runs
    to ``int``, so numbering is compared numerically rather than as text.
    ``re.split`` with a capturing group always alternates non-digit / digit, so
    two keys built this way compare like against like.

    Args:
        name: Sample name.  ``None`` is treated as the empty string.

    Returns:
        tuple: Key suitable for :func:`sorted`.
    """
    parts = re.split(r"(\d+)", str(name if name is not None else ""))
    return tuple(int(p) if p.isdigit() else p.lower() for p in parts)


def sort_samples(
    df,
    name_col: str = "samp_name",
    depth_col: str = "minimumDepthInMeters",
):
    """Order *df* by depth, then by natural sample-name order.

    Samples are written to every sheet in one order: shallowest first, samples
    with no recorded depth last, and ties (including all the depthless ones)
    broken by :func:`natural_key`.  Neotoma returns samples in neither order —
    for West Okoboji the depthless samples come back first, followed by the
    rest deepest-first — so each sheet has to impose this itself.

    Degrades to a no-op when *df* is empty or *name_col* is missing, and treats
    a missing *depth_col* as "no depths recorded", which falls through to name
    order.

    Args:
        df (pandas.DataFrame): Rows to order, one per sample.
        name_col (str): Column holding the sample name.  Defaults to
            ``"samp_name"``.
        depth_col (str): Column holding the sample depth.  Defaults to
            ``"minimumDepthInMeters"``.

    Returns:
        pandas.DataFrame: *df* reordered, with a fresh index.
    """
    if df.empty or name_col not in df.columns:
        return df

    depths = (
        pd.to_numeric(df[depth_col], errors="coerce")
        if depth_col in df.columns
        else pd.Series(float("nan"), index=df.index)
    )

    def key(index):
        depth = depths.at[index]
        missing = pd.isna(depth)
        # The leading flag is what puts depthless samples last; the placeholder
        # depth is never compared against a real one because of it.
        return (missing, 0.0 if missing else float(depth), natural_key(df.at[index, name_col]))

    return df.loc[sorted(df.index, key=key)].reset_index(drop=True)


def checklist_version(template_path) -> str | None:
    """Extract the FAIRe checklist version from a template filename.

    ``assets/FAIRe_checklist_v1.0.2.xlsx`` yields ``"1.0.2"``.  Reading it from
    the filename rather than hardcoding it means upgrading the template updates
    both the README stamp and the ``checkls_ver`` term.

    Args:
        template_path (str | pathlib.Path): Path to the FAIRe template.

    Returns:
        str | None: The version, or ``None`` when the name carries no ``vN…``
        component.
    """
    match = re.search(r"v(\d+(?:\.\d+)*)", Path(template_path).name)
    return match.group(1) if match else None
