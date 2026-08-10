"""Command-line interface for the neotoma2FAIRe conversion tool.

Entry point is :func:`main`, registered in ``pyproject.toml`` as
``neotoma2faire = "neotoma2faire.cli:main"``.

Usage examples::

    neotoma2faire template -d 55582
    neotoma2faire template -d 55582 -o my_output.xlsx
    neotoma2faire template -d 55582 -t assets/FAIRe_checklist_v1.0.2.xlsx
"""

import argparse

import neotoma2faire as ntf


def parse_args():
    """Parse command-line arguments for the neotoma2FAIRe tool.

    Returns:
        argparse.Namespace: Namespace with attributes:

        * ``tool`` (list[str]) — sub-command to run (currently only
          ``'template'``).
        * ``output`` (str | None) — output ``.xlsx`` path. When ``None``
          (default), :func:`~.make_template.make_template` writes to
          ``outputs/FAIRe_DS_<datasetid>.xlsx``.
        * ``template`` (str) — path to the base FAIRe template workbook.
          Defaults to ``./assets/FAIRe_checklist_v1.0.2.xlsx``.
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
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=None,
        help=(
            "Output .xlsx path. When omitted, the file is written to "
            "outputs/FAIRe_DS_<datasetid>.xlsx so the source template is "
            "never overwritten."
        ),
    )
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        required=False,
        default="./assets/FAIRe_checklist_v1.0.2.xlsx",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        default="55582",
        type=int,
        help="The Neotoma dataset for which FAIRe data is to be generated.",
    )
    parser.add_argument(
        "-e",
        "--env",
        default=None,
        choices=["prod", "dev", "local"],
        help=(
            "Which Neotoma API environment to hit. Defaults to NEOTOMA_API_ENV "
            "if set, otherwise 'prod'. Use 'dev' to talk to api-dev.neotomadb.org, "
            "or 'local' to talk to a local API server on localhost:3005 while "
            "testing endpoints that haven't shipped to production yet."
        ),
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help=(
            "Shortcut: load credentials from .env.dev and use the Neotoma "
            "development API. Without this flag, .env.production is loaded."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
        help="Show the program's version number and exit.",
    )
    return parser.parse_args()


def main():
    """Entry point: parse arguments and dispatch to the requested tool."""
    args = parse_args()

    # Load .env.dev or .env.production (default) before anything else reads
    # environment variables.
    from neotoma2faire.config import load_env
    load_env(use_dev=args.dev)

    # Explicit --env wins over --dev; otherwise --dev forces the dev API URL.
    if getattr(args, "env", None) in ("prod", "dev", "local"):
        from neotoma2faire.api.client import use_environment
        use_environment(args.env)
    elif args.dev:
        from neotoma2faire.api.client import use_environment
        use_environment("dev")

    if "template" in args.tool:
        ntf.make_template(args)
