from openpyxl import load_workbook
#from .modify_README import modify_README
#from .add_project import add_project
from .add_samples import add_samples

def make_template(args):
    wb = load_workbook(filename = args.template)

    #modify_README(newsheet)
    #add_project(newsheet, args.dataset)
    #add_samples(newsheet, args.dataset)
    df = add_samples(wb, args.dataset)
    #wb.save(args.output)
    df.to_csv('file.csv', index=False)
    return df