from datetime import datetime
import glob
import json
import os

import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm

import DataBUS.neotomaHelpers as nh
import DataBUS.neotomaValidator as nv
from DataBUS import Response
from DataBUS.neotomaHelpers.logging_dict import logging_response

"""Example script demonstrating the use of DataBUS functions.
This script serves as an example of how to use the DataBUS library to validate and upload data to a Neotoma database.
It includes steps for hashing files, checking validation logs, and validating various data types such as sites, geopolitical units, collection units, etc.
The script reads data from specified CSV files, validates the data against the Neotoma database, and logs the validation process.
It also includes error handling to ensure that any issues during validation are properly logged and that database transactions
are rolled back if necessary.

The script should be run twice, once with the --upload flag set to False to perform validation and generate logs, and a second time with the --upload flag set to True to upload the validated data to the database.

Run with uv
Example usage:
    uv run python dataBUSdata/aedna_databus.py --template='dataBUSdata/template.yml' --data='dataBUSdata/' --upload False
    uv run python dataBUSdata/aedna_databus.py --template='dataBUSdata/template.yml' --data='dataBUSdata/' --upload True
"""
# Extracted from DataBUS repository.

args = nh.parse_arguments()
load_dotenv()
connection = json.loads(os.getenv("PGDB_TANK"))

filenames = glob.glob(args["data"] + "*.csv")
yml_dict = nh.template_to_dict(temp_file=args["template"])

conn = psycopg2.connect(**connection, connect_timeout=5)
cur = conn.cursor()

start_time = datetime.now()
print(f"Start uploading at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

for filename in tqdm(filenames, desc="Files", unit="file"):
    conn.rollback()
    logfile = []
    databus = {'sites': Response()}

    csv_file = nh.read_csv(filename)
    hashcheck = nh.hash_file(filename)
    filecheck = nh.check_file(filename, validation_files="dataBUSdata/")

    logfile = logfile + hashcheck["message"] + filecheck["message"]
    logfile.append(f"\nNew Upload started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if hashcheck["pass"] is False and filecheck["pass"] is False:
        logfile.append("File must be properly validated before it can be uploaded.")
        hashcheck = False
    else:
        hashcheck = True

    try:
        logfile.append("=== Sites ===")
        # Site is already an existing Site
        databus['sites'].valid = [True]
        databus['sites'].id_int = 1766

        logfile.append("=== CUs ===")
        result = nh.safe_step(
            "collunits",
            lambda csv_file=csv_file, databus=databus: nv.valid_collunit(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["collunits"] = result
            logfile = logging_response(databus["collunits"], logfile)

        logfile.append("=== Analysis Units ===")
        result = nh.safe_step(
            "analysisunits",
            lambda csv_file=csv_file, databus=databus: nv.valid_analysisunit(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["analysisunits"] = result
            logfile = logging_response(databus["analysisunits"], logfile)

        logfile.append("=== Datasets ===")
        result = nh.safe_step(
            "datasets",
            lambda csv_file=csv_file, databus=databus: nv.valid_dataset(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["datasets"] = result
            logfile = logging_response(databus["datasets"], logfile)

        logfile.append("=== Database ===")
        result = nh.safe_step(
            "database",
            lambda databus=databus: nv.valid_dataset_database(
                cur=cur, yml_dict=yml_dict, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["database"] = result
            logfile = logging_response(databus["database"], logfile)
        
        logfile.append("=== Geochron Datasets ===")
        result = nh.safe_step(
            "geodataset",
            lambda csv_file=csv_file, databus=databus: nv.valid_geochron_dataset(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["geodataset"] = result
            logfile = logging_response(databus["geodataset"], logfile)

        logfile.append("=== Chronologies ===")
        result = nh.safe_step(
            "chronologies",
            lambda csv_file=csv_file, databus=databus: nv.valid_chronologies(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["chronologies"] = result
            logfile = logging_response(databus["chronologies"], logfile)

        logfile.append("=== Samples ===")
        result = nh.safe_step(
            "samples",
            lambda csv_file=csv_file, databus=databus: nv.valid_sample(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["samples"] = result
            logfile = logging_response(databus["samples"], logfile)

        logfile.append("=== Sample Ages ===")
        result = nh.safe_step(
            "sample_age",
            lambda csv_file=csv_file, databus=databus: nv.valid_sample_age(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["sample_age"] = result
            logfile = logging_response(databus["sample_age"], logfile)

        logfile.append("=== Data ===")
        result = nh.safe_step(
            "data",
            lambda csv_file=csv_file, databus=databus: nv.valid_data(
                cur=cur, yml_dict=yml_dict, csv_file=csv_file, databus=databus
            ), logfile, conn)
        if result is not None:
            databus["data"] = result
            logfile = logging_response(databus["data"], logfile)
        
        all_true = all(databus[key].validAll for key in databus)
        all_true = all_true and hashcheck
        if args['upload'] is True:
            up = ".upload.log"
            if all_true:
                # Don't have a PI so I will skip this step for now.
                #databus["finalize"] = nv.insert_final(cur, databus=databus)
                conn.commit()
                logfile.append("Data has been successfully uploaded to the database.")
            else:
                conn.rollback()
                logfile.append(
                    "Data must be fully validated before it can be uploaded to the database."
                )
        else:
            up = ".valid.log"
            if all_true:
                conn.rollback()
                logfile.append("Data has been fully validated and is ready for upload.")
            else:
                conn.rollback()
                logfile.append(
                    "Data has not passed validation. Please review the log messages for details."
                )
    except Exception as e:
        conn.rollback()
        logfile.append(f"An error occurred during validation: {str(e)}")
    with open(filename + up, "w", encoding="utf-8") as writer:
        for i in logfile:
            writer.write(i)
            writer.write("\n")
