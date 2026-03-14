from openpyxl import load_workbook
#from .modify_README import modify_README
#from .add_project import add_project
from .get_data import get_data
from .add_samples import add_samples
from .add_taxa import add_taxa

def make_template(args):
    wb = load_workbook(filename = args.template)

    #modify_README(newsheet)
    #add_project(newsheet, args.dataset)
    #add_samples(newsheet, args.dataset)
    data = get_data(args.dataset)
    smp = add_samples(wb, data)
    tx_ids = data['taxonid'].unique().tolist()
    tx = add_taxa(wb, tx_ids)
    #wb.save(args.output)

    # Okoboji Style
    df = tx.merge(smp, left_on='most_specific_id', right_on='taxonid',  how='left')
    df = df.drop(columns=['taxonid', 'most_specific_id', 'most_specific_name'])
    df.to_csv('trial_.csv', index=False)
    return df