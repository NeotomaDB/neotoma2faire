import argparse
import neotoma2faire as ntf

def parse_args():
    """Parse arguments if the script is run from the commandline.

    Returns:
        argparse.Namespace: A Namespace object defining the arguments passed from the commandline.
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
    args = parse_args()
    if "template" in args.tool:
        ntf.make_template(args)
