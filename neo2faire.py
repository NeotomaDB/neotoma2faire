import argparse
import neotoma2faire as ntf

def parse_args():  
    """_Parse arguments if the script is run from the commandline._

    Returns:
        _argparse.Namespace_: _A Namespace object defining the argunments passed from the commandline._
    """  
    parser = argparse.ArgumentParser(prog = "Neotoma2FAIRe Conversion Tool",
                                     description = "A Neotoma tool to help transform data between standard formats.",
                                     )
    parser.add_argument('tool',
                        nargs = 1,
                        help = 'The name of the neotoma2FAIRe tool to be used.',
                        choices=['template'],
                        default = 'template')
    parser.add_argument('-o', '--output',
                        type = str,
                        required = False,
                        default = 'template.xlsx')
    parser.add_argument('-t', '--template',
                        type = str,
                        required = False,
                        default = './assets/FAIRe_checklist_v1.0.2_FULLtemplate.xlsx')
    parser.add_argument('-d', '--dataset',
                        default = '1001',
                        type = int,
                        help = 'The Neotoma dataset for which FAIRe data is to be generated.')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s 1.0',
                        help='Show the program\'s version number and exit.')
    
    args = parser.parse_args()
    return args

def main(args):
    if 'template' in args.tool:
        workbook = ntf.make_template(args)


if __name__ == '__main__':
    args = parse_args()
else:
    # For testing in the Python environment:
    class args:
        tool = 'template'
        dataset = 1
        output = 'template.xlsx'
        template = './assets/FAIRe_checklist_v1.0.2_FULLtemplate.xlsx'

for j, k in vars(args).items():
    print(f'\t{j}: {k}')

main(args)
