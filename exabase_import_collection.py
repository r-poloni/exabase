# Script to import collection data from existing csv files

import csv
import sqlite3
import requests

connection = sqlite3.connect("example.db")

def get_usage_key_in_taxonomy(canonical_name):
    query = f"SELECT usageKey FROM taxonomy WHERE canonicalName = '{canonical_name}';"
    cursor = connection.cursor()
    cursor.execute(query)
    line = cursor.fetchall()
    if len(line) == 0:
        print(f"Error: no usageKey found in taxonomy for {line}")
        exit(1)
    if len(line) != 1:
        print(f"Error: More than one record found for {line}")
        exit(1)
    return line[0][0]

def scientific_name_from_collection(row):
    genus = row[3]
    species = row[4]
    subspecies = row[5]
    if subspecies != "" and subspecies!="NA":
        return f"{genus} {species} {subspecies}"
    elif species == "" or species=="NA":
        return f"{genus}"
    else:
        return f"{genus} {species}"

def fetch_linking_id(row):
    locality = row[10]
    usagekey = get_usage_key_in_taxonomy(scientific_name_from_collection(row))
    query = f"SELECT id FROM records WHERE usageKey = '{usagekey}' AND locality = '{locality}' AND eventDate = '{row[12]}' AND institutionID = 'coll. Poloni';"
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    if len(rows) == 0:
        return None
    if len(rows) != 1:
        print(f"Error: More than one record found for {row}")
        exit(1)
    return rows[0][0]

def compose_stateprovince(row):
   state = row[8]
   province = row[9]

   if province == "":
        return f"{state}"
   elif province == " ":
        return f"{state}"
   elif state == "":
        return f"{province}"
   elif state == " ":
        return f"{province}"
   else:
        return f"{state} {province}"

def insert_record(row):
    usageKey = get_usage_key_in_taxonomy(scientific_name_from_collection(row))
    countryCode = row[7]
    stateProvince = compose_stateprovince(row)
    locality = row[10]
    query = """
        INSERT INTO records (usageKey, identifiedBy, dateIdentified, identificationQualifier, typeStatus, num_m, num_f, num_nosex, num_mol, countryCode, stateProvince, locality, elevation, verbatimLatitude, verbatimLongitude, decimalLatitude, decimalLongitude, eventDate, recordedBy, biog_reg, institutionID, basisOfRecord, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
    values = (usageKey,'','','','','','','','',countryCode,stateProvince,locality,row[11],row[15],row[16],row[17],row[18],row[12],row[13],row[21],'coll. Poloni','PreservedSpecimen',row[25])
    cursor = connection.cursor()
    cursor.execute(query, values)
    id = cursor.lastrowid
    connection.commit()
    return id


def insert_molecular(row, linking_id):
    sex = row[6]
    query = f"""
        INSERT INTO molecular (collection_id, linking_id, sex, notes, lifeStage , bodypart, preservation, localisation)
        VALUES ('{row[0]}', {linking_id}, '{row[6]}','','{row[19]}','{row[20]}','{row[22]}', '{row[23]}');
        """
    cursor = connection.cursor()
    cursor.execute(query)
    # Determine which count to increment
    if sex == 'f':
        update_query = f"UPDATE records SET num_f = COALESCE(num_f, 0) + 1, num_mol = COALESCE(num_mol, 0) +1 WHERE rowid = {linking_id};"
    elif sex == 'm':
        update_query = f"UPDATE records SET num_m = COALESCE(num_m, 0) + 1, num_mol = COALESCE(num_mol, 0) +1 WHERE rowid = {linking_id};"
    else:
        update_query = f"UPDATE records SET num_nosex = COALESCE(num_nosex, 0) + 1, num_mol = COALESCE(num_mol, 0) +1 WHERE rowid = {linking_id};"

    cursor.execute(update_query)
    connection.commit()
    connection.commit()


def insert_sequences(row, collection_id):
    query = f"""
        INSERT INTO sequences (type, accession, collection_id)
        VALUES ('{row[24]}','','{row[0]}');
        """
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()


with open("collection_example_data.csv", mode="r", newline='', encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        linking_id = fetch_linking_id(row)
        collection_id = row[0]
        if linking_id == None:
            insert_record(row)
            linking_id = fetch_linking_id(row)
            insert_molecular(row, linking_id)
            insert_sequences(row, collection_id)
        else:
            insert_molecular(row, linking_id)
            insert_sequences(row, collection_id)
connection.close()
