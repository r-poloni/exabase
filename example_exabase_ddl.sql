--  EXABASE - A SQLITE3 DATABASE FPR HANDLING OCCURRENCE AND COLLECTION DATA FOR NATURAL HISTORY

--  Data Definition
--
--  First, you need to create a new SQLite database called "exabase"
--  In the command line type `sqlite3`. Then, when prompted with `sqlite>`, type `.save exabase.db`, and finally .exit.
--  You should now have a file named `exabase.db` in the current folder.
--  Now, you can run this script to create the tables and views in the database by typing `sqlite3 exabase.db < exabase_ddl.sql`.

-- INSTRUCTIONS TO FILL THE DATABASE
-- The fields with "NON NULL" flag must be filled, so genus, species, locality, eventDate and institutionID are mandatory fields
-- and create a unique combination of a species found at a place at a given moment and preserved in a given institution, that
-- represents the unit of the database (a record).
-- The "records" table is the master table, and has a unique ID (id) which is automatically generated that is used in the table 
-- "collection" to link the multiple specimens present in alcol collection to one record in the "records" table. The "collection"
-- table is then linked to the "sequences" table that contains the sequencing done on each alcol sample in "collection".
-- Another table, taxonomy, contains the taxonomical data for each name usage identified with a usageKey: family, order, author etc.
-- By filling the cells, the " ' " (apostrophe) character should be avoided because it is read by sqlite as a separator. Instead 
-- use a space or an exterisk that will not hamper the meaningfulness of the locality. 
-- Below a description of the fields


CREATE TABLE IF NOT EXISTS "records" (
	"id"	INTEGER UNIQUE, -- automatically generated
  "usageKey" TEXT, -- taxonomy, unique numeric key for this taxon in gbif backbone taxonomy, used to retrieve author and higher taxonomy 
  "identifiedBy" TEXT, -- who identified the specimen as belonging to the species reported
  "dateIdentified" TEXT, -- date of identification
  "identificationQualifier" TEXT, -- determiner's doubts about the identification, e.g. cfr.
  "typeStatus" TEXT, -- fill if the specimen is a type (either holotypus, paratypus, allotypus etc.)
  "num_m" INTEGER, -- number of males for this record
  "num_f" INTEGER, -- number of females
  "num_nosex" INTEGER, -- number of specimens for which the sex cannot be identified
  "num_mol" INTEGER, --number of samples available for molecular analysis
  "countryCode" TEXT, -- nation where the species was recorded, alpha-2 code according to ISO 3166
  "stateProvince" TEXT, -- region or province
  "locality"	TEXT NOT NULL, -- locality, i.e. all the toponyms not associated with a state or administrative region
  "elevation" INTEGER, -- altitude expressed in metres above sea level
  "verbatimLatitude" TEXT, -- latitude, verbatim as in the specimen label or exif data
  "verbatimLongitude" TEXT, -- longitude, verbatim as in the specimen label or exif data
  "decimalLatitude" TEXT, -- latitude, converted from verbatimLatitude or given based on toponym, always in decimal degrees
  "decimalLongitude" TEXT, -- longitude, converted from verbatimLongitude or given based on toponym, always in decimal degrees
  "eventDate"	TEXT NOT NULL, -- date of collection of the specimen / photo / observation
  "recordedBy" TEXT, -- collector or photographer or observed
  "biog_reg" TEXT, -- biogeographic region associated to the record
  "institutionID" TEXT NOT NULL, -- source, either museum or collection for specimens or site or other source
  "basisOfRecord" TEXT CHECK("basisOfRecord" = "PreservedSpecimen" OR "basisOfRecord" = "HumanObservation" OR "basisOfRecord" = "MaterialCitation"), -- either specimen, photo or observation
  "notes" TEXT, -- all that does not fit into the other fields, like habitat or the collecting technique (e.g. UV light, funnel trap)
  "image" TEXT, -- image of the specimen or record
	PRIMARY KEY("id" AUTOINCREMENT),
  UNIQUE (usageKey, locality, eventDate, recordedBy, institutionID),
  FOREIGN KEY (usageKey) REFERENCES taxonomy(usageKey)
);

CREATE TABLE IF NOT EXISTS "molecular" (
	"collection_id"	TEXT UNIQUE, -- ID of the specimen in the alcol collection
  "linking_id" INTEGER, -- ID of the record in "records" containing the occurrence data of the specimen
  "sex" TEXT, -- sex of the specimen if known, otherwise NA
  "notes" TEXT, -- all that does not fit into the other fields
  "lifeStage" TEXT CHECK("lifeStage" = "adult" OR "lifeStage" = "larva" OR "lifeStage" = "pupa" OR "lifeStage" = "egg"),
  "bodypart" TEXT, -- bodypart preserved (e.g whole body, or hind left leg)
  "preservation" TEXT, -- either ethanol 96, ethanol 70, snap frozen, collection (dry)) or collection (fixed in ethanol)
  "localisation" TEXT, -- place where the specimen is preserved
  "image" TEXT, -- image of the specimen
	PRIMARY KEY("collection_id"),
  FOREIGN KEY (linking_id) REFERENCES records(id)
);

CREATE TABLE IF NOT EXISTS "sequences" (
  "id"	INTEGER UNIQUE, -- unique, automatically generated 
  "type" TEXT NOT NULL, -- sequencing type (e.g. COI, Illumina, etc.)
  "accession" TEXT, -- ncbi accession
  "collection_id" TEXT, -- collection id, refers to "collection" table
  PRIMARY KEY("id" AUTOINCREMENT),
  FOREIGN KEY (collection_id) REFERENCES molecular(collection_id)
);

CREATE TABLE IF NOT EXISTS "taxonomy" (
  "id"	INTEGER UNIQUE, -- unique, automatically generated
  "usageKey" TEXT UNIQUE, -- unique key for this taxon in gbif backbone taxonomy, used to retrieve author and higher taxonomy. If added manually is preceded by a "m" 
  "order" TEXT, -- taxonomy, order of the species
  "family" TEXT, -- taxonomy, family of the species
  "subfamily" TEXT, -- taxonomy, subfamily of the species
  "tribe" TEXT, -- taxonomy, tribe of the species
  "genus" TEXT, -- taxonomy, genus
  "species" TEXT, --taxonomy, species name (genus + species)
  "canonicalName" TEXT, -- taxonomy, full scientific name without authorship
  "authorship" TEXT, -- taxonomy, authorship associated to the name usage (scientificName)
  "scientificName" TEXT, -- taxonomy, full scientific name wit authorship that creates a name usage in gbif
  "rank" TEXT, -- rank of the name usage, i.e. in our case species or subspecies
  "isInGBIF" INTEGER CHECK("isInGBIF" = 0 OR "isInGBIF" = 1), -- binary, 0 or 1, 1 = name usage present in gbif, 0 = not present (added manually)
  PRIMARY KEY("id" AUTOINCREMENT),
  UNIQUE(usageKey)
);
