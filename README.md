## ESX Tool v3
Command line tool for manipulating contents of Ekahau .ESX files

Example use cases:

- Extract static AP radio configuration into CSV for conversion into WLC CLI
- Normalize ESX contents (e.g. AP naming convention) prior to Catalyst Center map upload
- Swap Ekahau map images - update images with different sizes and reposition APs based on alignment points

Tested on Ekahau AI Pro 11.4 / 11.5 / 11.6 / 11.7 / 11.8 / 11.9

Note: Ekahau data structures may change over time, support for older Ekahau versions may be broken as newer versions are added

Python 3.10+

### Install

```
pip install -r requirements.txt
```

The original .esx file is never modified in place - ESX Tool extracts it to a
temporary directory and writes a new file alongside the original, named
`<project>.esxtool.esx`.

### Command line options

Exactly one option must be given per invocation.

#### --mapswap
```
esxtool.py --mapswap \path-to\project.esx \path-to\map-file.esx
```
- Repositions APs from _project_ esx file, using image from _map_ esx file (creating new esx file)
- Images can be of different resolution
- Floorplans must have the same name within Ekahau, supports multiple floorplan replacement simultaneously
- Both .esx files need TWO matching floor alignment points for each floorplan
- Re-aligns all APs based on coordinates calculated from alignment points
- Floor alignment points are consumed (deleted) during the process

Step-by-step:
- In project ESX file, add **two** alignment points on the map
- Create a separate ESX file with only a new map image - image size can be different to project ESX, but the map should be depicting the same area
- Add **two** matching reference points to the map ESX file
- ESXTool will create a third ESX file, with the APs from the project file repositioned onto the image from the map file
- Map names must match in Ekahau

Alignment point rules (enforced before any AP is moved - if a floor fails these
checks the tool reports the floor name and exits without writing a new file):
- Each matched floorplan must have exactly two alignment points, in both the project and the map ESX file
- The two points must differ in both X and Y - points placed in a straight horizontal or vertical line are rejected

Caveats
- Will rescale/reposition APs only, not survey paths, areas, or any other Ekahau objects
- __Does not__ work on Ekahau projects containing both measured and simulated APs
- __May not__ work with maps that have been rotated using the Ekahau map rotate feature, rotate the image before importing into Ekahau
- __May not__ work when map images are of different types, e.g. replacing a .png with a .pdf, this may be related more to Ekahau itself

#### --esxtocsv
```
esxtool.py --esxtocsv \path-to\project.esx
```
- Dumps survey information to CSV, from specified ESX file
- Parses both _Simulated_ and _Measured_ Ekahau files (but not both simultaneously)
- Saves two CSV files next to the ESX file, AP data & map/floor data:
  `<project>-APs.csv` and `<project>-Floors.csv`
- AP data includes up to four radio slots per AP (channel, tx power, antenna height/tilt/direction/type)

#### --alltocsv
```
esxtool.py --alltocsv
```
- Dumps survey information to CSV, from all ESX files in current working directory
- Parses both _Simulated_ and _Measured_ Ekahau files (but not both simultaneously)
- Saves two combined CSV files in the current directory, AP data & map/floor data:
  `All-APs.csv` and `All-Floors.csv`

#### --csvtoesx
```
esxtool.py --csvtoesx \path-to\template.csv \path-to\project.esx
```
- Updates ESX file using data from CSV template (note: CSV path first, ESX path second)
- Changes AP names and X/Y map coordinates
- Will update AP name if new name is provided
- Will update X/Y coordinates if new coordinates are provided (only if AP already has coordinates in Ekahau)
- Writes the result to a new `<project>.esxtool.esx` file

#### --template
```
esxtool.py --template
```
Generates empty CSV template (`esxtool-template.csv`) in the current directory,
used when importing into ESX with `--csvtoesx`

### License

This software is licensed under the Cisco Sample Code License

URL: https://developer.cisco.com/site/license/cisco-sample-code-license/
