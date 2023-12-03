## ESX Tool v2
Command line tool for manipulating contents of Ekahau .esx files

Extracts ESX information to CSV / Updates ESX from CSV

Example use case: Normalize ESX contents (e.g. AP Names) prior to DNA-C map upload

Verified on Ekahau AI Pro 11.4.0.1

### Command line options

#### --tocsv [.esx file]

Dumps AP information from ESX to CSV

Parses both _Simulated_ and _Measured_ Ekahau files (but not both combined)

Saves two CSV files, AP data & map/floor data

#### --fromcsv [.esx file] [.csv file]

Updates ESX file using data from CSV template

Changes AP names and X/Y map coordinates

Will update AP name if new name is provided

Will update X/Y coordinates if new coordinates are provided (only if AP already has coordinates in Ekahau)

#### --template

Generates empty CSV template, used when importing into ESX
