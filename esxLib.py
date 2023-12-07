import os
import json

import colorama

from messageLib import *


class Ap():

    def __init__(self, id):

        self.id = id
        self.slots = {}


class Floor():

    def __init__(self, id):

        self.id = id


all_aps = []
all_floors = []


def read_esx(json_path):

    read_floors_plans(json_path)
    read_reference_points(json_path)
    read_access_points(json_path)
    read_simulated_radios(json_path)
    read_antenna_types(json_path)
    read_measured_radios(json_path)
    read_access_point_measurements(json_path)
    
    return all_aps, all_floors


def read_floors_plans(json_path):

    with open(os.path.join(json_path, "floorPlans.json"), "r") as f:
        floors = json.load(f)

    for item in floors["floorPlans"]:
        floor = Floor(item["id"])
        floor.name = item["name"]
        floor.width = item["width"]
        floor.height = item["height"]
        floor.image = item["imageId"]
        floor.scaling = item["metersPerUnit"]
        floor.points = ""

        all_floors.append(floor)


def read_reference_points(json_path):

    try:
        with open(os.path.join(json_path, "referencePoints.json"), "r") as f:
            reference_points = json.load(f)
    except FileNotFoundError:
        info()
        print(f"Not found: {colorama.Fore.YELLOW}referencePoints.json{colorama.Fore.RESET}")
    else:
        for reference in reference_points["referencePoints"]:
            for point in reference["projections"]:
                x = round(float(point["coord"]["x"]), 1)
                y = round(float(point["coord"]["y"]), 1)
                floor_index = next((index for index, floor in enumerate(all_floors) if floor.id == point["floorPlanId"]), None)
                all_floors[floor_index].points += f"({x}:{y})" 


def read_access_points(json_path):

    with open(os.path.join(json_path, "accessPoints.json"), "r") as f:
        access_points = json.load(f)

    for item in access_points["accessPoints"]:
        if item["status"] != "DELETED":
            ap = Ap(item["id"])
            ap.name = item["name"]
            ap.mac = ""
            ap.ssid = ""
            try:
                ap.vendor = item["vendor"]
            except KeyError:
                ap.vendor = ""
            try:
                ap.model = item["model"]
            except KeyError:
                ap.model = ""
            try:
                ap.location_x = round(item["location"]["coord"]["x"])
            except KeyError:
                ap.location_x = ""
            try:
                ap.location_y = round(item["location"]["coord"]["y"])
            except KeyError:
                ap.location_y = ""
            try:
                ap.location_id = item["location"]["floorPlanId"]
                ap.location_name = next(floor.name for floor in all_floors if floor.id == ap.location_id)
            except KeyError:
                ap.location_id = ""
                ap.location_name = ""
            
            all_aps.append(ap)


def read_simulated_radios(json_path):

    try:
        with open(os.path.join(json_path, "simulatedRadios.json"), "r") as f:
            radios = json.load(f)
    except FileNotFoundError:
        info()
        print(f"Not found: {colorama.Fore.YELLOW}simulatedRadios.json{colorama.Fore.RESET}")
    else:
        for item in radios["simulatedRadios"]:
            for ap in all_aps:
                if ap.id == item["accessPointId"]:
                    ap.ekahau = "Simulated"
                    if item["radioTechnology"] != "BLUETOOTH": #Exclude Bluetooth radios
                        slot_config = {}
                        slot_config[item["accessPointIndex"]] = {}
                        try:
                            slot_config[item["accessPointIndex"]]["channel"] = freq_to_channel(item["channelByCenterFrequencyDefinedNarrowChannels"][0])
                        except IndexError:
                            slot_config[item["accessPointIndex"]]["channel"] = 0
                            info()
                            print("Simulated radio does not have channel, setting to 0")
                        slot_config[item["accessPointIndex"]]["antennaid"] = item["antennaTypeId"]
                        slot_config[item["accessPointIndex"]]["antennamounting"] = item["antennaMounting"]
                        slot_config[item["accessPointIndex"]]["antennaheight"] = round(item["antennaHeight"], 1)
                        slot_config[item["accessPointIndex"]]["antennatilt"] = round(item["antennaTilt"])
                        slot_config[item["accessPointIndex"]]["antennadirection"] = item["antennaDirection"]
                        slot_config[item["accessPointIndex"]]["enabled"] = item["enabled"]
                        if item["enabled"]:
                            slot_config[item["accessPointIndex"]]["txpower"] = round(item["transmitPower"])
                        else:
                            slot_config[item["accessPointIndex"]]["txpower"] = 0

                        ap.slots = {**ap.slots, **slot_config}


def read_antenna_types(json_path):

    try:
        with open(os.path.join(json_path, "antennaTypes.json"), "r") as f:
            antennas = json.load(f)
    except FileNotFoundError:
        info()
        print(f"Not found: {colorama.Fore.YELLOW}antennaTypes.json{colorama.Fore.RESET}")
    else:
        for ap in all_aps:
            for slot, config in ap.slots.items():
                try:
                    ap.slots[slot]["antennatype"] = next((item["name"] for item in antennas["antennaTypes"] if item["id"] == config["antennaid"]), "NA")
                except KeyError:
                    ap.slots[slot]["antennatype"] = "NULL"
                    info()
                    print("Antenna does not have name, setting to NULL")

    
def freq_to_channel(freq):

    if str(freq).startswith("2"):
        return int((freq - 2405) / 5)
    elif str(freq).startswith("5"):
        return int((freq / 5) - 1000)
    elif str(freq).startswith(("6", "7")):
        pass


def read_measured_radios(json_path):

    try:
        with open(os.path.join(json_path, "measuredRadios.json"), "r") as f:
            measured = json.load(f)
    except FileNotFoundError:
        info()
        print(f"Not found: {colorama.Fore.YELLOW}measuredRadios.json{colorama.Fore.RESET}")
    else:
        for radio in measured["measuredRadios"]:
            for ap in all_aps:
                if radio["accessPointId"] == ap.id:
                    ap.measuredradio = radio["accessPointMeasurementIds"][0] #Save first found measurement id


def read_access_point_measurements(json_path):

    try:
        with open(os.path.join(json_path, "accessPointMeasurements.json"), "r") as f:
            measurements = json.load(f)
    except FileNotFoundError:
        info()
        print(f"Not found: {colorama.Fore.YELLOW}accessPointMeasurements.json{colorama.Fore.RESET}")
    else:
        for measurement in measurements["accessPointMeasurements"]:
            for ap in all_aps:
                if measurement["id"] == ap.measuredradio:
                    ap.ssid = measurement["ssid"]
                    ap.mac = measurement["mac"]
                    ap.ekahau = "Measured"





