"""Command-line interface for the neotoma2FAIRe conversion tool.

Entry point is :func:`main`, registered in ``pyproject.toml`` as
``neotoma2faire = "neotoma2faire.cli:main"``.

Usage examples::

    neotoma2faire template -d 55582 -t assets/FAIRe_checklist_v1.0.2_FULLtemplate.xlsx
    neotoma2faire template -d 55582 -o my_output.xlsx
"""

import argparse
import neotoma2faire as ntf


def parse_args():
    """Parse command-line arguments for the neotoma2FAIRe tool.

    Returns:
        argparse.Namespace: Namespace with attributes:

        * ``tool`` (list[str]) — sub-command to run (currently only
          ``'template'``).
        * ``output`` (str) — output ``.xlsx`` path (default
          ``'template.xlsx'``).
        * ``template`` (str) — path to the base FAIRe template workbook.
        * ``dataset`` (int) — Neotoma dataset ID (default ``55582``).
    """
    parser = argparse.ArgumentParser(
        prog="Neotoma2FAIRe Conversion Tool",
        description="A Neotoma tool to help transform data between standard formats.",
    )
    parser.add_argument(
        "tool",
        nargs=1,
        help="The name of the neotoma2FAIRe tool to be used.",
        choices=["template"],
        default="template",
    )
    parser.add_argument("-o", "--output", type=str, required=False, default="template.xlsx")
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        required=False,
        default="./assets/FAIRe_checklist_v1.0.2_FULLtemplate.xlsx",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        default="55582",
        type=int,
        help="The Neotoma dataset for which FAIRe data is to be generated.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 1.0",
        help="Show the program's version number and exit.",
    )
    return parser.parse_args()


def main():
    """Entry point: parse arguments and dispatch to the requested tool."""
    args = parse_args()
    if "template" in args.tool:
        ntf.make_template(args)
