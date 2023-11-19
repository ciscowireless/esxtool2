"""
ESX Tool v2
Command line tool for manipulating contents of Ekahau .ESX files
Extracts ESX information into CSV / Updates ESX from CSV
Example use case: Normalize ESX contents (e.g. AP Names) prior to DNA-C map upload

Verified on Ekahau AI Pro 11.4.0.1

"""
import os
import argparse

import colorama

from messageLib import *
from fileIoLib import *
from esxLib import *


def file_path(file_path):

    if not os.path.isfile(file_path):
        raise ValueError()
    else:
        return file_path


def start():

    parser = argparse.ArgumentParser(description=f"\n{colorama.Fore.CYAN}ESX Tool{colorama.Fore.RESET} Version 2 - ESX file manipuilation tool")
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument("--tocsv", help="Specify ESX file", type=file_path, metavar="ESX")
    parser_group.add_argument("--fromcsv", help="Specify ESX file and CSV file", nargs=2, type=file_path, metavar=('ESX', 'CSV'))  
    parser_group.add_argument("--template", help="Generate empty CSV template", action="store_true")
    args = parser.parse_args()

    if args.template:
        make_empty_csv()

    elif args.tocsv:
        path_init_esx([args.tocsv][0])
        EsxTool.aps, EsxTool.floors = read_esx(EsxTool.temp_path)
        save_csv_aps(EsxTool.aps, EsxTool.esx_dir, EsxTool.esx_file)
        save_csv_floors(EsxTool.floors, EsxTool.esx_dir, EsxTool.esx_file)
        remove_temp(EsxTool.temp_path)

    elif args.fromcsv:
        path_init_esx(args.fromcsv[0])
        EsxTool.csv_data = read_csv(args.fromcsv[1])
        write_esx(EsxTool.csv_data, EsxTool.temp_path)
        zip_esx(EsxTool.temp_path, EsxTool.esx_dir, EsxTool.esx_file)
        remove_temp(EsxTool.temp_path)
        

def path_init_esx(esx_path):

    full_esx_path = os.path.abspath(esx_path)
    EsxTool.esx_dir = os.path.dirname(full_esx_path)
    EsxTool.esx_file = os.path.basename(full_esx_path)
    ok()
    print(f"ESX file: {colorama.Fore.GREEN}{EsxTool.esx_file}{colorama.Fore.RESET}")
    ok()
    print(f"ESX location: {colorama.Fore.GREEN}{EsxTool.esx_dir}{colorama.Fore.RESET}")
    EsxTool.temp_path = unzip_esx(full_esx_path)


class EsxTool():

    def run():

        colorama.init()
        start()


if __name__ == "__main__":

    EsxTool.run()
