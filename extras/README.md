#### Supporting scripts used for Cisco Live

These scripts are part of a larger deployment process, they are crude and of no value on their own.

**aprename2025.py**

Renames APs according to naming convention.

Takes ESXTool --tocsv output, as input

Creates separate AP name file that can be used as ESXTool --from CSV input

Renames based on pre-defined AP model, AP height, and map name

**m4cli.py**

Takes ESXTool --tocsv output, as input

Creates 9800 CLI for configuring 9104 beamwidths as per Ekahau project






