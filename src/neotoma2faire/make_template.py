from openpyxl import load_workbook
from .modify_README import modify_README
from .add_project import add_project

def make_template(args):
    newsheet = load_workbook(filename = args.template)

    modify_README(newsheet)
    add_project(newsheet, args.dataset)
    newsheet.save(args.output)
    return newsheet