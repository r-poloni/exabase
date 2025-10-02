import csv
import sqlite3
import requests

connection = sqlite3.connect("example.db")

def scientific_name(row):
   genus = row[3]
   species = row[5]
   subspecies = row[6]

   if subspecies != "" and subspecies!="NA":
        return f"{genus} {species} {subspecies}"
   elif species == "" or species=="NA":
        return f"{genus}"
   else:
        return f"{genus} {species}"


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

def compose_locality(row):
   locality1 = row[16]
   locality2 = row[17]

   if locality2 == "":
        return f"{locality1}"
   elif locality2 == " ":
        return f"{locality1}"
   else:
        return f"{locality1} {locality2}"

def import_records():
  with open("records_example_data.csv", mode="r", newline='', encoding="utf-8") as file:
      reader = csv.reader(file)
      # Skip the first row
      next(reader, None)
      for row in reader:
        stateProvince = row[14] + " " + row[15]
        locality = compose_locality(row)
        usageKey = get_usage_key_in_taxonomy(scientific_name(row))
        query = """
        INSERT INTO records (usageKey, identifiedBy, dateIdentified, identificationQualifier, typeStatus, num_m, num_f, num_nosex, num_mol, countryCode, stateProvince, locality, elevation, verbatimLatitude, verbatimLongitude, decimalLatitude, decimalLongitude, eventDate, recordedBy, biog_reg, institutionID, basisOfRecord, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        values = (usageKey, row[8], '', '', row[9], row[10], row[11], row[12], '', row[13], stateProvince, locality, row[18], row[19], row[20], row[21], row[22], row[24], row[26], row[23], row[25], row[27], row[28])
        connection = sqlite3.connect("example.db")
        connection.cursor().execute(query, values)
        connection.commit()


import_records()