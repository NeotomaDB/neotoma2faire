"""Orchestrate the FAIRe template generation workflow.

:func:`make_template` ties together all data-fetch and data-write steps:
it loads the base Excel workbook, retrieves Neotoma data, pivots samples and
taxa, merges the two tables, and writes the result to a CSV (the Excel-save
path is prepared but commented out pending full sheet-write implementation).
"""

from openpyxl import load_workbook

from .get_data import get_data
from .add_samples import add_samples
from .add_taxa import add_taxa


def make_template(args):
    """Generate a FAIRe-format template for a given Neotoma dataset.

    Loads the base Excel workbook, fetches all data for *args.dataset* via
    :func:`~.get_data.get_data`, pivots samples with
    :func:`~.add_samples.add_samples`, builds the taxonomic hierarchy with
    :func:`~.add_taxa.add_taxa`, merges the two DataFrames on
    ``most_specific_id`` ↔ ``taxonid``, and writes a trial CSV.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.  Expected
            attributes:

            * ``template`` (str) — path to the base FAIRe ``.xlsx`` file.
            * ``dataset`` (int) — Neotoma dataset ID to process.
            * ``output`` (str) — destination path for the saved workbook
              (used when the Excel-save path is re-enabled).

    Returns:
        pandas.DataFrame: Merged taxa × sample DataFrame written to
        ``trial_.csv``.
    """
    wb = load_workbook(filename=args.template)

    # modify_README(wb)
    # add_project(wb, args.dataset)
    data = get_data(args.dataset)
    smp = add_samples(wb, data)
    tx_ids = data['taxonid'].unique().tolist()
    tx = add_taxa(wb, tx_ids)
    # wb.save(args.output)

    # Okoboji Style
    df = tx.merge(smp, left_on='most_specific_id', right_on='taxonid', how='left')
    df = df.drop(columns=['taxonid', 'most_specific_id', 'most_specific_name'])
    df.to_csv('trial_.csv', index=False)
    return df
