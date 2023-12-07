import os
import csv 
import json
import os
import shutil
import zipfile

import colorama

from messageLib import *

CSV_TEMPLATE = ["AP Name", "New AP Name", "New Floor X", "New floor Y"]


def make_empty_csv():

    filename = os.path.join(os.getcwd(), "esxtool-template.csv")
    try:
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(CSV_TEMPLATE)
    except PermissionError:
        no()
        print(f"Error creating CSV template")
    else:
        ok()
        print(f"Created CSV template: {colorama.Fore.GREEN}{filename}{colorama.Fore.RESET}")


def unzip_esx(esx_file):

    extract_dir = os.path.join(os.path.dirname(esx_file), "esxtool-temp")
    try:
        os.mkdir(extract_dir)
    except FileExistsError:
        info()
        print("Temp directory already exists, not re-creating")
    with zipfile.ZipFile(esx_file, 'r') as zip:
        zip.extractall(path=extract_dir)
        ok()
        print(f"ESX file extracted to: {colorama.Fore.GREEN}{extract_dir}{colorama.Fore.RESET}")
    return(extract_dir)


def zip_esx(extracted_esx_path, zip_file_path, esx_file):
    
    zip_contents = os.listdir(extracted_esx_path)
    zip_file_name = f"{esx_file[:-4]}.esxtool.esx"
    zip_location = os.path.join(zip_file_path, zip_file_name)
    
    with zipfile.ZipFile(zip_location, 'w') as zip:
        for item in zip_contents:
            zip.write(os.path.join(extracted_esx_path, item), arcname=item, compress_type=zipfile.ZIP_DEFLATED)
    ok()
    print(f"Reconstructed ESX file: {colorama.Fore.GREEN}{os.path.join(zip_file_path, zip_file_name)}{colorama.Fore.RESET}")


def remove_temp(extracted_esx_path):

    shutil.rmtree(extracted_esx_path)
    ok()
    print(f"Removed temp directory: {colorama.Fore.GREEN}{extracted_esx_path}{colorama.Fore.RESET}")


def save_csv_aps(aps, filepath, filename):

    headings = [
                "AP Name",
                "Floor",
                "Floor X",
                "Floor Y",
                "Ekahau AP Type",
                "Model",
                "MAC Address",
                "SSID"
    ]            
    slot_headings = [
                    "Slot",
                    "Enabled",
                    "Channel",
                    "TxPower",
                    "Height",
                    "Tilt",
                    "Antenna"
    ]
    headings += 4 * slot_headings #Add CSV columns for up to 4 radio slots

    filename = filename.split(".")[0] + "-APs.csv"
    csv_path = os.path.join(filepath, filename)
    try:
        with open(csv_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headings)
            ap_count = 0
            for ap in aps:
                ap_count += 1
                row = [ap.name, ap.location_name, ap.location_x, ap.location_y, ap.ekahau, ap.model, ap.mac, ap.ssid]
                for slot in sorted(ap.slots):
                    row.append(slot)
                    row.append(ap.slots[slot]["enabled"])
                    row.append(ap.slots[slot]["channel"])
                    row.append(ap.slots[slot]["txpower"])
                    row.append(ap.slots[slot]["antennaheight"])
                    row.append(ap.slots[slot]["antennatilt"])
                    row.append(ap.slots[slot]["antennatype"])
                csvwriter.writerow(row)
    except PermissionError:
        no()
        print(f"Error writing to CSV file")
    else:
        ok()
        print(f"Exported {colorama.Fore.GREEN}{ap_count}{colorama.Fore.RESET} AP(s) to CSV: {colorama.Fore.GREEN}{csv_path}{colorama.Fore.RESET}")


def save_csv_floors(floors, filepath, filename):

    headings = [
                "Name",
                "ImageId",
                "Width",
                "Height",
                "Scaling (m/unit)",
                "ReferencePoint 1",
                "ReferencePoint 2",
                "ReferencePoint 3"
    ]
    filename = filename.split(".")[0] + "-Floors.csv"
    csv_path = os.path.join(filepath, filename)
    try:
        with open(csv_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headings)
            floor_count = 0
            for floor in floors:
                floor_count += 1
                row = [floor.name, floor.image, floor.width, floor.height, floor.scaling]
                csvwriter.writerow(row)
    except PermissionError:
        no()
        print(f"Error writing to CSV file")
    else:
        ok()
        print(f"Exported {colorama.Fore.GREEN}{floor_count}{colorama.Fore.RESET} floor(s) to CSV: {colorama.Fore.GREEN}{csv_path}{colorama.Fore.RESET}")


def read_csv(csv_path):

    count, noxy_count = 0, 0
    csv_data = []
    with open(csv_path) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if row == CSV_TEMPLATE:
                continue
            count += 1
            apname = str(row[0])
            newname = str(row[1])
            try:
                newx = float(row[2])
                newy = float(row[3])
            except ValueError:
                noxy_count += 1
                newx, newy = "", ""

            csv_data.append({"apname" : apname, "newname": newname, "newx": newx, "newy": newy})    
    ok()
    print(f"Read {colorama.Fore.GREEN}{count}{colorama.Fore.RESET} AP(s) from CSV")
    return csv_data


def write_esx(csv_data, json_path):

    with open(os.path.join(json_path, "accessPoints.json"), "r") as f:
        ap_json = json.load(f)

    name_count, coord_count = 0, 0
    for ap in ap_json["accessPoints"]:
        index = next((index for index, csv in enumerate(csv_data) if csv["apname"] == ap["name"]), None)
        if index != None:
            new_name = csv_data[index]["newname"]
            if new_name != "":
                name_count += 1
                ap_json["accessPoints"][ap_json["accessPoints"].index(ap)].update({"name": new_name})
        
        if ap.get("location"):
            newx = csv_data[index]["newx"]
            newy = csv_data[index]["newy"]
            if newx != "" and newy != "":
                coord_count += 1
                ap_json["accessPoints"][ap_json["accessPoints"].index(ap)]["location"]["coord"].update({"x": newx})
                ap_json["accessPoints"][ap_json["accessPoints"].index(ap)]["location"]["coord"].update({"y": newy})

    with open(os.path.join(json_path, "accessPoints.json"), "w") as f:
        json.dump(ap_json, f, indent=2)
    
    ok()
    print(f"{colorama.Fore.GREEN}{name_count}{colorama.Fore.RESET} AP(s) changed names")
    ok()
    print(f"{colorama.Fore.GREEN}{coord_count}{colorama.Fore.RESET} AP(s) changed coordinates")

