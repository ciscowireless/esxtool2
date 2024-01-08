"""
ESX Tool v2
Command line tool for manipulating contents of Ekahau .ESX files
Extracts ESX information into CSV / Updates ESX from CSV
Example use case: Normalize ESX contents (e.g. AP Names) prior to DNA-C map upload

Verified on Ekahau AI Pro 11.4 / 11.5

Added image swap function, replaces & rescales map from 2nd ESX file, based on alignment points

"""
import os
import argparse

import colorama

from messageLib import *
from fileIoLib import *
from esxLib import *
from mapLib import *


def file_path(file_path):

    if not os.path.isfile(file_path):
        raise ValueError()
    else:
        return file_path


def run(EsxTool):

    parser = argparse.ArgumentParser(description=f"\n{colorama.Fore.CYAN}ESX Tool{colorama.Fore.RESET} Version 2 - ESX file manipuilation tool")
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument("--tocsv", help="Specify ESX file", type=file_path, metavar="ESX")
    parser_group.add_argument("--fromcsv", help="Specify ESX file and CSV file", nargs=2, type=file_path, metavar=('ESX', 'CSV'))  
    parser_group.add_argument("--template", help="Generate empty CSV template", action="store_true")
    parser_group.add_argument("--mapreplace", help="Replace & rescale ESX map from new ESX", nargs=2, type=file_path, metavar=("ESX", "Map-ESX"))
    args = parser.parse_args()

    if args.template:
        make_empty_csv()

    elif args.tocsv:
        EsxTool.esx_dir, EsxTool.esx_file, EsxTool.temp_path = path_init_esx([args.tocsv][0])
        read_esx_floors(EsxTool.floors, EsxTool.temp_path)
        read_esx_aps(EsxTool.aps, EsxTool.floors, EsxTool.temp_path)
        save_csv_aps(EsxTool.aps, EsxTool.esx_dir, EsxTool.esx_file)
        save_csv_floors(EsxTool.floors, EsxTool.esx_dir, EsxTool.esx_file)
        remove_temp(EsxTool.temp_path)

    elif args.fromcsv:
        EsxTool.esx_dir, EsxTool.esx_file, EsxTool.temp_path = path_init_esx(args.fromcsv[0])
        EsxTool.csv_data = read_csv(args.fromcsv[1])
        write_esx(EsxTool.csv_data, EsxTool.temp_path)
        zip_esx(EsxTool.temp_path, EsxTool.esx_dir, EsxTool.esx_file)
        remove_temp(EsxTool.temp_path)
    
    elif args.mapreplace:
        EsxTool.esx_dir, EsxTool.esx_file, EsxTool.temp_path = path_init_esx(args.mapreplace[0])
        EsxTool.map_esx_dir, EsxTool.map_esx_file, EsxTool.map_temp_path = path_init_esx(args.mapreplace[1])
        read_esx_floors(EsxTool.floors, EsxTool.temp_path)
        read_esx_floors(EsxTool.map_floors, EsxTool.map_temp_path)
        read_esx_aps(EsxTool.aps, EsxTool.floors, EsxTool.temp_path)
        rescale_maps(EsxTool.floors, EsxTool.map_floors, EsxTool.aps, EsxTool.temp_path, EsxTool.map_temp_path)
        zip_esx(EsxTool.temp_path, EsxTool.esx_dir, EsxTool.esx_file)
        remove_temp(EsxTool.temp_path)
        remove_temp(EsxTool.map_temp_path)


def path_init_esx(esx_path):

    full_esx_path = os.path.abspath(esx_path)
    esx_dir = os.path.dirname(full_esx_path)
    esx_file = os.path.basename(full_esx_path)
    ok()
    print(f"ESX file: {colorama.Fore.GREEN}{esx_file}{colorama.Fore.RESET}")
    ok()
    print(f"ESX location: {colorama.Fore.GREEN}{esx_dir}{colorama.Fore.RESET}")
    temp_path = unzip_esx(full_esx_path)

    return esx_dir, esx_file, temp_path


class EsxTool2():

    def __init__(self):

        colorama.init()

        self.aps = []
        self.floors = []
        self.map_floors = []
    
        run(self)


if __name__ == "__main__":

    EsxTool2()
