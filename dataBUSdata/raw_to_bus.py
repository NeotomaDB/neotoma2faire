### To clean data for Okoboji style template
# To upload using DataBUS

import pandas as pd

try:
    data = pd.read_csv('dataBUSdata/og/Toy_Okoboji.csv')
except Exception as e:
    data = pd.read_excel('dataBUSdata/orig/WLO18S_Okoboji.xlsx', sheet_name='asv_counts')
    age_depths = pd.read_excel('dataBUSdata/orig/WLO18S_Okoboji.xlsx', sheet_name='age_depth')

wl_cols = [col for col in data.columns if col.startswith('WL')]
other_cols = [col for col in data.columns if not col.startswith('WL')]
taxa_cols = [col for col in other_cols if col not in ['ASV', 'Total', 'Reference_Sequences']]

cols = ['ASV'] + wl_cols
data = data[cols].dropna(subset=['ASV'])

data = data.set_index('ASV').transpose().reset_index()
data = data.rename(columns={'index': 'SampleName'})
data.columns.name = None

# After transpose, columns are taxon names; capture them before adding metadata
taxon_cols = [c for c in data.columns if c != 'SampleName']

# Because the site exists, to simplify the process
data['siteid'] = 1766
data['sitename'] = 'West Okoboji Lake'
data['handle'] = 'Toy-oko'
data['cu_notes'] = 'Toy DS to handle DNA samples'
data['eventData'] = '2026-03-13'

data['Units'] = "NISP"

## Chronologies
data['AgeModel'] = "CRS"
data['AgeType'] = "Calendar years BP"

#data['GeochronType'] = "Lead-210"

# Sedimentation rate derived from column name
data['SedRateUnits'] = "cm/yr"

# Merge age_depths if they exist
if 'age_depths' in locals():
    data = data.merge(age_depths, left_on='SampleName', right_on='Sample Name', how='left')
    # if col1 is a string, that looks like 1-2 , make the conversion 2-1 = 1 and take that float value as the Plot depth
    data['Thickness(cm)'] = data['Sample interval (cm)'].apply(lambda x: float(x.split('-')[1]) - float(x.split('-')[0]) if isinstance(x, str) and '-' in x else x)


# Reorder columns to match the expected format
expected_cols = ['siteid', 'sitename', 'handle', 'cu_notes',
                 'SampleName', 'eventData', 'CRS (Calendar year)',
                 'Sample interval (cm)', 'Plot depth (cm)', 
                 'Thickness(cm)', 'Sa cm/yr.', 'Units',
                 'AgeModel', 'AgeType', 'SedRateUnits'
                 ] + taxon_cols
data = data[expected_cols]
data = data.rename(columns={
    'CRS (Calendar year)': 'CRS(CalendarYear)',
    'Sample interval (cm)': 'SampleInterval(cm)',
    'Plot depth (cm)': 'PlotDepth(cm)',
    'Sa cm/yr.': 'SedimentationRate(cm-yr)'
})
data.to_csv('dataBUSdata/Toy_Okoboji_DBUS.csv', index=False)
