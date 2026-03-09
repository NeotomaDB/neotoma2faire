from datetime import datetime
from .neo_connect import neo_connect
from .utils import apply_query_result

def add_project(workbook, datasetid):
    ws = workbook.active = workbook['projectMetadata']
    conn = neo_connect()

    celltodict = []
    keys = []
    for i in range(1, ws.max_column + 1):
        keys.append(ws.cell(1, i).value)

    for row in range(2, ws.max_row + 1):
        tempdict = {}
        for i in range(1, ws.max_column + 1):
            tempdict[keys[i-1]] = ws.cell(row, i).value
        celltodict.append(tempdict)
    projectinfo = """
        SELECT ds.datasetid AS datasetid,
            array_agg(DISTINCT dpi_contact.contactname) as "recordedBy",
            array_agg(DISTINCT dpi.contactid) as "recordedByID",
            array_agg(DISTINCT ct.contactname) as project_contact,
            array_agg(DISTINCT inst.institutionname) as institution,
            array_agg(DISTINCT inst.institutionID) as "institutionID",
            pj.projectname AS project_name,
            pj.projectid AS project_id
        FROM ndb.datasets AS ds
        LEFT OUTER JOIN ndb.datasetpis AS dpi ON dpi.datasetid = ds.datasetid
        LEFT OUTER JOIN ndb.contacts AS dpi_contact ON dpi_contact.contactid = dpi.contactid
        LEFT OUTER JOIN ndb.projectdatasets AS pd ON pd.datasetid = ds.datasetid
        LEFT OUTER JOIN ndb.projects AS pj ON pj.projectid = pd.projectid
        LEFT OUTER JOIN ndb.projectparticipants as pp on pp.projectid = pd.projectid 
        LEFT OUTER JOIN ndb.contacts as ct on ct.contactid = pp.contactid
        LEFT OUTER JOIN ndb.projectgrants AS pg ON pg.projectid = pj.projectid
        LEFT OUTER JOIN ndb.grants AS gr ON gr.grantid = pg.grantid
        LEFT OUTER JOIN ndb.fundinginstitutions as fi on fi.grantid = gr.grantid
        LEFT OUTER JOIN ndb.institutions as inst on inst.institutionid = fi.institutionid
        WHERE ds.datasetid = %(datasetid)s
        GROUP BY ds.datasetid, pj.projectid, pj.projectname;
    """
    with conn.cursor() as cur:
        _ = cur.execute(projectinfo, {'datasetid': datasetid})
        result = cur.fetchall()
    term_row_map = {entry['term_name']: j for j, entry in enumerate(celltodict)}

    def write_project(_row_idx, j, value):
        celltodict[j]['project_level'] = value
        ws.cell(j + 2, 4, value=value) # j + 2 because of header row and 1-based indexing

    apply_query_result(result, term_row_map, write_project, none_placeholder='emptyvalue')

    datamgmt = """SELECT
                    1 AS checkls_ver,
                    ds.recdatemodified AS mod_date,
                    'http://creativecommons.org/licenses/by/4.0/legalcode' AS license,
                    ARRAY_AGG(pub.doi) ON bibliographicCitation,
                    ARRAY_AGG(extdb.urlmask || extd.identifier) AS associated_resource
                  FROM
                    ndb.datasets AS ds
                    LEFT OUTER JOIN ndb.datasetpublications AS dsp ON dsp.datasetid = ds.datasetid
                    LEFT OUTER JOIN ndb.publications AS pub ON pub.publicationid = dsp.publicationid
                    LEFT OUTER JOIN ndb.externaldatasets AS extd ON extd.datasetid = ds.datasetid
                    LEFT OUTER JOIN ndb.externaldatabases AS extdb ON extdb.databaseid = extd.extdatabaseid
                  WHERE ds.datasetid = %(datasetid)s
                  GROUP BY ds.datasetid, ds.recdatemodified;
    """

    return workbook