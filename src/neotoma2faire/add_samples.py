from datetime import datetime
from .neo_connect import neo_connect

def add_samples(workbook, datasetid):
    ws = workbook.active = workbook['sampleMetadata']
    conn = neo_connect()

    celltodict = []
    keys = []

    for i in range(1, ws.max_row + 1):
        keys.append(ws.cell(i, 1).value)

    for col in range(1, ws.max_column + 1):
        tempdict = {}
        for i in range(1, ws.max_row + 1):
            tempdict[keys[i-1]] = ws.cell(i, col).value
        celltodict.append(tempdict)

    samples = """
        SELECT
            distinct smp.samplename AS samp_name,
            'sample' AS samp_category,
            string_agg(distinct gpu.geopoliticalname, '; ') AS geo_loc_name,
            cu.colldate AS event_date,
            cu.colldevice AS samp_collect_device,
            st.altitude AS elev,
            au.depth AS minimumDepthInMeters,
            au.depth AS maximumDepthInMeters,
            lp.value AS tot_depth_water_col
        FROM ndb.datasets AS ds
            INNER JOIN ndb.samples AS smp ON smp.datasetid = ds.datasetid
            INNER JOIN ndb.collectionunits AS cu ON cu.collectionunitid = ds.collectionunitid
            inner join ndb.analysisunits as au on (au.collectionunitid = cu.collectionunitid and au.analysisunitid = smp.analysisunitid)
            INNER JOIN ndb.sites AS st ON st.siteid = cu.siteid
            INNER JOIN ndb.sitegeopolitical AS sgp ON sgp.siteid = st.siteid
            INNER JOIN ndb.geopoliticalunits AS gpu ON gpu.geopoliticalid = sgp.geopoliticalid
            LEFT JOIN ndb.lakeparameters AS lp ON (lp.siteid = st.siteid AND lp.lakeparameterid = 1)
        WHERE ds.datasetid = %(datasetid)s
        GROUP BY ds.datasetid, smp.sampleid, au.analysisunitid, cu.colldate, cu.colldevice, st.altitude, lp.value;
    """
    
    with conn.cursor() as cur:
        _ = cur.execute(samples, {'datasetid': datasetid})
        result = cur.fetchall()

    for i in result:
        for k in i.keys():
            for j in range(len(celltodict)):
                if celltodict[j]['samp_name'] == k:
                    celltodict[j]['value'] = i[k]
                    print(i[k])
                    print(celltodict[j])
                    if isinstance(i[k], list):
                        value = '; '.join([s for s in i[k] if s is not None])
                    else:
                        value = i[k] or 'AHAHA'
                        ws.cell(j,4, value = value)