from openpyxl import load_workbook
from .modify_README import modify_README
from .add_project import add_project
from .add_samples import add_samples

def make_template(args):
    newsheet = load_workbook(filename = args.template)

    modify_README(newsheet)
    add_project(newsheet, args.dataset)
    add_samples(newsheet, args.dataset)
    newsheet.save(args.output)
    return newsheet