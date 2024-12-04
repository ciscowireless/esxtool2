## ESX Tool v2.1
Command line tool for manipulating contents of Ekahau .ESX files

Example use cases:

- Extract static AP radio configuration into CSV for conversion into WLC CLI
- Normalize ESX contents (e.g. AP naming convention) prior to Catalyst Center map upload
- Swap Ekahau map images - update images with different sizes and reposition APs based on alignment points

Tested on Ekahau AI Pro 11.4 / 11.5 / 11.6

### Command line options

#### --mapreplace
```
esxtool2.py --mapreplace \path-to\project.esx \path-to\map-file.esx
```
- Repositions APs from _project_ esx file, using image from _map_ esx file (creating new esx file)
- Images can be of different resolution
- Floorplans must have the same name within Ekahau, supports multiple floorplan replacement simultaneously
- Both .esx files need TWO matching floor alignment points for each floorplan
- Re-aligns all APs based on coordinates calculated from alignment points
- Floor alignment points are consumed (deleted) during the process

Step-by-step:
- In project ESX file, add TWO alignment points on the map
- Create a separate ESX file with only a new map image - image size can be different to project ESX, but the map should be depicting the same area
- Add TWO matching reference points to the map ESX file
- ESXTool will create a third ESX file, with the APs from the project file repositioned on the image from the new map file
- Map names must match in Ekahau, all matching map names will be rescaled

#### --tocsv
```
esxtool2.py --tocsv \path-to\project.esx
```
- Dumps AP information from ESX to CSV
- Parses both _Simulated_ and _Measured_ Ekahau files (but not both simultaneously)
- Saves two CSV files, AP data & map/floor data

#### --fromcsv
```
esxtool2.py --fromcsv \path-to\project.esx \path-to\template.csv
```
- Ipdates ESX file using data from CSV template
- Changes AP names and X/Y map coordinates
- Will update AP name if new name is provided
- Will update X/Y coordinates if new coordinates are provided (only if AP already has coordinates in Ekahau)

#### --template
```
esxtool2.py --template
```
Generates empty CSV template, used when importing into ESX

### License

This software is licensed under the Cisco Sample Code License

URL: https://developer.cisco.com/site/license/cisco-sample-code-license/
