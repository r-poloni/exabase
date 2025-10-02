# exabase

Exabase is an SQLite-based database solution for storing natural history collections data suited for unifying under the same database structure both occurrence-based data (e.g. citizen science observations) where multiple specimens are lumped together and specimen-based data (e.g. a collection of samples for barcoding) where each specimen is recorded separately. 
It is completely open-source and linked to a shiny-based app to visualize the data: link
You will find below an example of how it can be used, taken by a paper I published and where we used both specimens from museums and citizen science and specimens for molecular analysis to study the distribution and taxonomy of a beetle genus.

## Data definition language explained

The file for data definition language is example_exabase_ddl.sql
The database is composed by 4 tables: “Records”, “Molecular”, “Taxonomy” and “Sequences”.

**Records:** it is a table where the unit is an occurrence, as in GBIF, so a row where multiple specimens can be stored. Each row of the table corresponds to a unique combination of taxon key (a unique identifier for that name usage as in GBIF usageKey), location, date, collector and institution holding the specimen or record (or source in case of bibliographic data or another database).
Here I put all data that come from any natural history collection or any other source: material I examine in museums, species occurrence from bibliographic source, occurrence from another database. For example, these two rows are separate because the collection date is different. Since specimens in collections are not usually identified by a unique code, it is pointless to enter a row for each specimen. Instead, we can enter a row for each series of specimens that are in the same place (collection), collected by the same person, in the same location and on the same date and that are stored in the same museum.
usageKey locality eventDate recordedBy institutionID
12174952 “Mt. Cimone” “1998-06-10” “P. Pallino” “Milan Museum of Natural History”
12174952 “Mt. Cimone” “2003-07-19” “P. Pallino” “Milan Museum of Natural History”

**Molecular:** this table contains my collection of molecular samples, and the specimens from other collections, where each specimen has a unique code and is stored separately. Here, all fields can be repeated except for the specimen identifier (collection_id)
For this table, the only thing I indicate is where the specimen is in the collection, how it is preserved, etc. but I don’t include data on locality, collection date and so on. Since the specimens in my collection are also a source of data on the distribution, phenology and biology of the species, they are also included in the ‘Records’ table. In the ‘Records’ table, obviously, a row will be a series of specimens taken on the same day, by the same person, etc., while in the ‘Collection’ table each specimen has a separate row. These two tables are linked by the ‘linking_id’ field, which, for each row in the “Collection” table, points to a row in the ‘Records’ table. In the example below, you can see that the linking_id is the same; in fact, both specimens point to the same row in the ‘Records’ table, which means that they are both specimens taken on the same day by me in the same locality.
collection_id linking_id preservation 
“RP24.001” 123 “alcol 96” “drawer 1.3”
“RP245.002” 123 “dry” “drawer 1.3”

**Taxonomy:** A third table includes the information on taxonomy: genus, species, author, family, etc. An example is shown below.
usageKey family genus canonicalName authorship
4458531 “Oedemeridae” “Oedemera” “Oedemera flavipes” “(Fabricius, 1792)”
12174952 “Cerambycidae” “Rhagium” “Rhagium inquisitor” “(Linnaeus, 1758)”

**Sequences:** This last table contains information on sequencing performed on the specimens contained in the “Molecular” table. Every record in this table is linked to the “Molecular” table with the “collection_id”.
id type collection_id
1 “COI” “RP24.014”
2 “COI” “RP24.015”

## Installation instructions

To install sqlite, please refer to your OS instructions, as in some cases it is already installed. To create the database, you can either use the command line or, if you are not familiar with it, you can use [DB Browser for SQLite](https://sqlitebrowser.org/), which is an open-source GUI for creating, modifying and visualizing SQLite databases. If you use this program, open DB Browser and follow these steps:

Click on "New Database" on the top left corner:
<img width="750" height="445" alt="scr_1" src="https://github.com/user-attachments/assets/4f172369-34a8-489f-b4cf-ca6ee9705dd1" />

DB Broser will ask for a name. Type it and store the database in an appropriate folder.
<img width="750" height="443" alt="scr_2" src="https://github.com/user-attachments/assets/0ec6469f-e5f1-41c4-a90e-78573cbbafab" />

Now DB Browser will ask you to create a table, click on "cancel" because we want to create it using our code:
<img width="750" height="445" alt="scr_3" src="https://github.com/user-attachments/assets/11236a56-f5c0-44a5-8d12-c8d315c4284b" />

Click on "execute SQL" and paste the code contained in the file "example_exabase_ddl.sql", then click on the small triangle to execute the code. The program console should output "Execute with success" or comething similar:
<img width="750" height="444" alt="scr_4" src="https://github.com/user-attachments/assets/42bb0603-8e88-45bc-b8bc-b5abd3c61a44" />


## Populating the database

Once the database has been created you will need to fill it with data. You can write data into the database as you want, but, given the many foreign keys and the necessity to update fields when you add data (e.g. when you add a specimen into the "Molecular" table, the "Records" table must be updated as well) I strongly advice you to do it automatically. 
The order of filling is very important, because otherwise the contraints put on the database foreign keys to prevent corrupting the database will not be respected. The first table to be filled in "Taxonomy" which is the backbone that allows the database to be linked to species names. Then you should fill "Records", "Molecular" and at the end "Sequences". 
What I do (but you can find your own way) is registering my data in two open office files, one for "Records", and one for "Molecular", that correspond to the two database tables and then use python code to populate the database. However, they can also be simpler tables that you modify on the fly while importing. As an example, I provide two tables: "reconrds_example_data.csv" and "molecular_example_data.csv". 
Two python scripts can be used to automatically update the "Taxonomy" table with new taxa: "exabase_update_taxonomy_for_records.py" and "exabase_update_taxonomy_for_molecular.py". They parse the table and read the species names, match them with the names already in "Taxonomy", and if they don't find a match, they interrogate the GBIF backbone taxonomy to find a usageKey for the new species added. If nothing is found, the usageKey will be set as the species name to allow adding the species to the table. However, this usage key is temporary, and it should be changed before uploading any new data on the other tables. In the example given, the species "Stenostoma rostratum" is not occurring in GBIF and has the usageKey m1.
Other two python scripts import the data into the database: "exabase_import_records.py" and "exabase_import_molecular.py". They parse the data, and populate the "Records" and "Molecular" tables. 
