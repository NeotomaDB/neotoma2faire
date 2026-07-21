"""Orchestrate the FAIRe template generation workflow.

:func:`make_template` ties together all data-fetch and data-write steps:

1. Loads the base FAIRe Excel workbook (the template).
2. Stamps the README sheet with version and timestamp.
3. Populates the ``projectMetadata`` sheet (PIs, institution, license, citations).
4. Fetches all data for the requested dataset via the Neotoma REST API.
5. Writes per-sample rows to the ``sampleMetadata`` sheet.
6. Writes taxonomic hierarchy rows to ``taxaFinal`` and ``taxaRaw``.
7. Writes minimal rows to ``experimentRunMetadata``.
8. Saves the populated workbook to *args.output* — this is the only
   deliverable.
"""

from pathlib import Path

from openpyxl import load_workbook

from .extract.data import get_data
from .write.experiment_run import add_experiment_run
from .write.project import add_project
from .write.readme import modify_README
from .write.samples import add_samples
from .write.taxa import add_taxa


def make_template(args):
    """Generate a FAIRe-format template for a given Neotoma dataset.

    Loads the base Excel workbook, fetches all data for *args.dataset* via the
    Neotoma REST API, populates every sheet that can be filled from Neotoma,
    and saves the workbook to *args.output*.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.  Expected attributes:

            * ``template`` (str) — path to the base FAIRe ``.xlsx`` file.
            * ``dataset`` (int) — Neotoma dataset ID to process.
            * ``output`` (str | None) — destination path for the populated
              workbook.  When ``None`` (the default from
              :mod:`~.cli`), the file is written to
              ``outputs/FAIRe_DS_<datasetid>.xlsx`` so the source template at
              ``args.template`` is never overwritten.

    Returns:
        str: The output path that was written.
    """
    # Default output to outputs/FAIRe_DS_<datasetid>.xlsx if not specified.
    if not args.output:
        args.output = f"outputs/FAIRe_DS_{args.dataset}.xlsx"
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(filename=args.template)

    modify_README(wb)
    add_project(wb, args.dataset)

    data = get_data(args.dataset)
    add_samples(wb, data) # sample metaData ; missing storage_df= keyword

    tx_ids = data["taxonid"].dropna().astype(int).unique().tolist()
    add_taxa(wb, tx_ids) # writes taxaFinal + taxaRaw; missing dataset_id= keyword

    add_experiment_run(wb, data)                     # writes experimentRunMetadata
    # add_amp_data(wb, args.dataset)
    # add_std_data(wb, args.dataset)
    # add_elow_quant(wb, args.dataset)
    # add_dropdown_values(wb)
    # otu pivot returned by add_samples is discarded ← no CSV written

    wb.save(args.output)
    return args.output
