"""
ESX Tool v2.1
Command line tool for manipulating contents of Ekahau .ESX files

Example use cases: 
- Extract static AP radio configuration into CSV for conversion into WLC CLI
- Normalize ESX contents (e.g. AP naming convention) prior to Catalyst Center map upload
- Swap Ekahau map images - update images with different sizes and reposition APs based on alignment points

Tested on Ekahau AI Pro 11.4 / 11.5 / 11.6

https://github.com/ciscowireless/esxtool2


Copyright (c) 2024 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
import os
import argparse

import colorama

from messageLib import Status
from fileIoLib import FileIo
from esxLib import Esx
from mapLib import Maps


class EsxTool2():

    def __init__(self):

        colorama.init()

        self.aps = []
        self.floors = []
        self.map_floors = []

        self.map_match = True
    
        self.status = Status()
        self.file_io = FileIo()
        self.esx = Esx()
        self.maps = Maps()

        self.run()


    def path_init_esx(self, file_path, path_type):

        full_path = os.path.abspath(file_path)
        match path_type:
            case "ESX":
                self.esx_file = os.path.basename(full_path)
                self.esx_dir = os.path.dirname(full_path)
                print(f"{self.status.ok}ESX file: {colorama.Fore.GREEN}{self.esx_file}{colorama.Fore.RESET}")
                print(f"{self.status.ok}ESX location: {colorama.Fore.GREEN}{self.esx_dir}{colorama.Fore.RESET}")
                self.temp_path = self.file_io.unzip_esx(full_path)
            case "MAP":
                self.map_esx_file = os.path.basename(full_path)
                self.map_esx_dir = os.path.dirname(full_path)
                print(f"{self.status.ok}MAP file: {colorama.Fore.GREEN}{self.map_esx_file}{colorama.Fore.RESET}")
                print(f"{self.status.ok}MAP location: {colorama.Fore.GREEN}{self.map_esx_dir}{colorama.Fore.RESET}")
                self.map_temp_path = self.file_io.unzip_esx(full_path)

    
    def file_path(self, file_path):

        if not os.path.isfile(file_path):
            raise ValueError()
        else:
            return file_path


    def run(self):

        parser = argparse.ArgumentParser(description=f"\n{colorama.Fore.CYAN}ESX Tool{colorama.Fore.RESET} Version 2.1 - ESX file manipuilation tool")
        parser_group = parser.add_mutually_exclusive_group(required=True)
        parser_group.add_argument("--tocsv", help="Specify ESX file", type=self.file_path, metavar="ESX")
        parser_group.add_argument("--fromcsv", help="Specify ESX file and CSV file", nargs=2, type=self.file_path, metavar=('ESX', 'CSV'))  
        parser_group.add_argument("--template", help="Generate empty CSV template", action="store_true")
        parser_group.add_argument("--mapreplace", help="Replace & rescale ESX map from new ESX", nargs=2, type=self.file_path, metavar=("ESX", "Map-ESX"))
        args = parser.parse_args()

        if args.template:
            self.file_io.make_empty_csv()

        elif args.tocsv:
            self.path_init_esx([args.tocsv][0], "ESX")
            self.esx.read_esx_floors(self.floors, self.temp_path)
            self.esx.read_esx_aps(self.aps, self.floors, self.temp_path)
            self.file_io.save_csv_aps(self.aps, self.esx_dir, self.esx_file)
            self.file_io.save_csv_floors(self.floors, self.esx_dir, self.esx_file)
            self.file_io.remove_temp(self.temp_path)

        elif args.fromcsv:
            self.path_init_esx(args.fromcsv[0], "ESX")
            self.csv_data = self.file_io.read_csv(args.fromcsv[1])
            self.file_io.write_esx(self.csv_data, self.temp_path)
            self.file_io.zip_esx(self.temp_path, self.esx_dir, self.esx_file)
            self.file_io.remove_temp(self.temp_path)
        
        elif args.mapreplace:
            self.path_init_esx(args.mapreplace[0], "ESX")
            self.path_init_esx(args.mapreplace[1], "MAP")
            self.esx.read_esx_floors(self.floors, self.temp_path)
            self.esx.read_esx_floors(self.map_floors, self.map_temp_path)
            self.esx.read_esx_aps(self.aps, self.floors, self.temp_path)
            self.maps.rescale_maps(self.floors, self.map_floors, self.aps, self.temp_path, self.map_temp_path)
            if self.maps.map_match: self.file_io.zip_esx(self.temp_path, self.esx_dir, self.esx_file)
            self.file_io.remove_temp(self.temp_path)
            self.file_io.remove_temp(self.map_temp_path)


if __name__ == "__main__":

    EsxTool2()
