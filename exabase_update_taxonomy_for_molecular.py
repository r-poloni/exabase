import csv
import sqlite3
import requests

connection = sqlite3.connect("example_exabase.db")

def get_species_gbif_taxonomy(usagekey):
    """
    Calls the GBIF species usageKey API with the given usagekey found using the function get_species_gbif_usage_key, to retrieve infos from
    gbif backbone taxonomy like genus, family, authorship etc. for a given usageKey
    See for details on taxonKey, usageKey, speciesKey,  https://discourse.gbif.org/t/understanding-gbif-taxonomic-keys-usagekey-taxonkey-specieskey/3045
    API documentation: https://techdocs.gbif.org/en/openapi/v1/species#/Species/getNameUsage

    Args:
        usagekey (str): The usagekey field from records

    Returns:
        string: order, family and authorship.
    """
    url = f"https://api.gbif.org/v1/species/{usagekey}"
    try:
        response = requests.get(url)  # Sending GET request
        response.raise_for_status()  # Raise error if status code is not 200
        data = response.json() # Convert return JSON response as a dictionary
        order = data.get('order')
        family = data.get('family')
        subfamily = ''
        tribe = ''
        genus = data.get('genus')
        subgenus = ''
        species = data.get('species')
        canonicalName = data.get('canonicalName')
        authorship = data.get('authorship')
        scientificName = data.get('scientificName')
        rank = data.get('rank')
        isInGBIF = '1'
        return order, family, subfamily, tribe, genus, subgenus, species, canonicalName, authorship, scientificName, rank, isInGBIF
    except requests.exceptions.RequestException as e:
        print(f"Error fetching species match: {e}")
        return 'NA','NA','NA','NA','NA','NA','NA','NA','NA','NA', 'NA','0'

def get_species_gbif_usage_key(name):
    """
    Calls the GBIF species match API with the given name (genus and species and subspecies if present) and returns the usageKey (the unique code in gbif backbone taxonomy for a taxon).
    See for details on taxonKey, usageKey, speciesKey,  https://discourse.gbif.org/t/understanding-gbif-taxonomic-keys-usagekey-taxonkey-specieskey/3045
    API documentation: https://techdocs.gbif.org/en/openapi/v1/species#/Searching%20names/matchNames

    Args:
        name (str): The scientific name of the species (genus+species+subspecies if there is one).

    Returns:
        string: usageKey.
    """
    url = "https://api.gbif.org/v1/species/match"
    params = {"name": name, "strict":"true"}  # Dictionary of query parameters
    try:
        response = requests.get(url, params=params)  # Sending GET request
        response.raise_for_status()  # Raise error if status code is not 200
        data = response.json() # Convert return JSON response as a dictionary
        return str(data.get('usageKey', ''))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching species match: {e}")
        exit(1)

def get_usage_key_in_taxonomy(canonical_name):
    canonical_name_collection = scientific_name_from_collection(row)
    query = f"SELECT usageKey FROM taxonomy WHERE canonincalName = '{canonical_name_collection}';"
    cursor = connection.cursor()
    cursor.execute(query)
    line = cursor.fetchall()
    if len(rows) == 0:
        return None
    if len(rows) != 1:
        print(f"Error: More than one record found for {row}")
        exit(1)
    return rows[0][0]

def fetch_usage_key_in_taxonomy(usagekey):
    query = f"SELECT * FROM taxonomy WHERE usageKey = '{usagekey}';"
    cursor = connection.cursor()
    cursor.execute(query)
    line = cursor.fetchall()
    if len(line) != 0:
        return line[0]
    else:
        return None

def insert_taxonomy(usageKey, order, family, subfamily, tribe, genus, subgenus, species, canonicalName, authorship, scientificName, rank, isInGBIF):
    query = f"""
        INSERT INTO taxonomy (usageKey, "order", family, subfamily, tribe, genus, subgenus, species, canonicalName, authorship, scientificName, rank, isInGBIF)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
    values = (usageKey, order, family, subfamily, tribe, genus, subgenus, species, canonicalName, authorship, scientificName, rank, isInGBIF)
    cursor = connection.cursor()
    cursor.execute(query,values)
    connection.commit()

def insert_taxonomy_tmp(usagekey_tmp):
    query = f"""
        INSERT INTO taxonomy (usageKey, "order", family, subfamily, tribe, genus, subgenus, species, canonicalName, authorship, scientificName, rank, isInGBIF)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
    values = (usagekey_tmp, '', '','', '', '', '', '', '', '', '', '', '0')
    cursor = connection.cursor()
    cursor.execute(query,values)
    connection.commit()

def scientific_name_from_collection(row):
    genus = row[3]
    species = row[5]
    subspecies = row[6]
    if subspecies != "":
        return f"{genus} {species} {subspecies}"
    else:
        return f"{genus} {species}"

with open("molecular_example_data.csv", mode="r", newline='', encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        usagekey = get_species_gbif_usage_key(scientific_name_from_collection(row))
        if usagekey != '':
            usage_key_in_taxonomy = fetch_usage_key_in_taxonomy(usagekey)
            if usage_key_in_taxonomy is None:
                from_gbif = get_species_gbif_taxonomy(usagekey)
                order = from_gbif[0]
                family = from_gbif[1]
                subfamily = from_gbif[2]
                tribe = from_gbif[3]
                genus = from_gbif[4]
                subgenus = from_gbif[5]
                species = from_gbif[6]
                canonicalName = scientific_name_from_collection(row)
                authorship = from_gbif[8]
                scientificName = from_gbif[9]
                rank = from_gbif[10]
                isInGBIF = from_gbif[11]
                insert_taxonomy(usagekey, order, family, subfamily, tribe, genus, subgenus, species, species, canonicalName, authorship, scientificName, rank, isInGBIF)
            else:
                print("usagekey already present")
        else:
            usagekey_tmp = scientific_name_from_collection(row)
            usage_key_in_taxonomy = fetch_usage_key_in_taxonomy(usagekey_tmp)
            if usage_key_in_taxonomy is None:
                insert_taxonomy_tmp(usagekey_tmp)
            else:
                print("usagekey_tmp already present")