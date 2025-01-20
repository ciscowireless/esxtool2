import os
import json

import colorama

from messageLib import Status
status = Status()


class Ap():

    def __init__(self, id):

        self.id = id
        self.slots = {}


class Floor():

    def __init__(self, id):

        self.id = id


class Esx():


    def __init__(self):

        self.status = Status()


    def read_esx_aps(self, esx_aps, esx_floors, json_path):

        read_access_points(esx_aps, esx_floors, json_path)
        read_simulated_radios(esx_aps, json_path)
        read_antenna_types(esx_aps, json_path)
        read_measured_radios(esx_aps, json_path)
        read_access_point_measurements(esx_aps, json_path)


    def read_esx_floors(self, esx_floors, json_path):

        read_floors_plans(esx_floors, json_path)
        read_reference_points(esx_floors, json_path)
    

def read_floors_plans(esx_floors, json_path):

    with open(os.path.join(json_path, "floorPlans.json"), "r") as f:
        floors = json.load(f)

    for item in floors["floorPlans"]:
        floor = Floor(item["id"])
        floor.name = item["name"]
        floor.width = item["width"]
        floor.height = item["height"]
        floor.image = item["imageId"]
        floor.scaling = item["metersPerUnit"]
        floor.points = []

        esx_floors.append(floor)


def read_reference_points(esx_floors, json_path):

    try:
        with open(os.path.join(json_path, "referencePoints.json"), "r") as f:
            reference_points = json.load(f)

    except FileNotFoundError:
        print(f"{status.info}Not found: {colorama.Fore.YELLOW}referencePoints.json{colorama.Fore.RESET}")
    else:
        for reference in reference_points["referencePoints"]:
            for point in reference["projections"]:
                x = round(point["coord"]["x"])
                y = round(point["coord"]["y"])
                floor_index = next((index for index, floor in enumerate(esx_floors) if floor.id == point["floorPlanId"]), None)
                esx_floors[floor_index].points.append([x,y])


def read_access_points(esx_aps, esx_floors, json_path):

    try:
        with open(os.path.join(json_path, "accessPoints.json"), "r") as f:
            access_points = json.load(f)

    except FileNotFoundError:
        print(f"{status.info}Not found: {colorama.Fore.YELLOW}accessPoints.json{colorama.Fore.RESET}")
    else:
        for item in access_points["accessPoints"]:
            if item["status"] != "DELETED":
                ap = Ap(item["id"])
                ap.name = item["name"]
                ap.hidden = item["hidden"]
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
                    ap.location_name = next(floor.name for floor in esx_floors if floor.id == ap.location_id)
                except KeyError:
                    ap.location_id = ""
                    ap.location_name = ""
                try:
                    ap.colour = item["color"]
                except KeyError:
                    ap.colour = ""
            
                esx_aps.append(ap)


def read_simulated_radios(esx_aps, json_path):

    try:
        with open(os.path.join(json_path, "simulatedRadios.json"), "r") as f:
            radios = json.load(f)

    except FileNotFoundError:
        print(f"{status.info}Not found: {colorama.Fore.YELLOW}simulatedRadios.json{colorama.Fore.RESET}")
    else:
        for item in radios["simulatedRadios"]:
            for ap in esx_aps:
                if ap.id == item["accessPointId"]:
                    ap.ekahau = "Simulated"
                    if item["radioTechnology"] != "BLUETOOTH": #Exclude Bluetooth radios
                        slot_config = {}
                        slot_config[item["accessPointIndex"]] = {}
                        try:
                            slot_config[item["accessPointIndex"]]["channel"] = freq_to_channel(item["channelByCenterFrequencyDefinedNarrowChannels"][0])
                        except (KeyError, IndexError):
                            slot_config[item["accessPointIndex"]]["channel"] = 0
                            print(f"{status.info}Simulated radio does not have channel, setting to 0")
                        slot_config[item["accessPointIndex"]]["antennaid"] = item["antennaTypeId"]
                        slot_config[item["accessPointIndex"]]["antennamounting"] = item["antennaMounting"]
                        slot_config[item["accessPointIndex"]]["antennaheight"] = round(item["antennaHeight"], 1)
                        slot_config[item["accessPointIndex"]]["antennatilt"] = round(item["antennaTilt"])
                        slot_config[item["accessPointIndex"]]["antennadirection"] = round(item["antennaDirection"])
                        slot_config[item["accessPointIndex"]]["enabled"] = item["enabled"]
                        if item["enabled"]:
                            slot_config[item["accessPointIndex"]]["txpower"] = round(item["transmitPower"])
                        else:
                            slot_config[item["accessPointIndex"]]["txpower"] = 0

                        ap.slots = {**ap.slots, **slot_config}


def read_antenna_types(esx_aps, json_path):

    try:
        with open(os.path.join(json_path, "antennaTypes.json"), "r") as f:
            antennas = json.load(f)

    except FileNotFoundError:
        print(f"{status.info}Not found: {colorama.Fore.YELLOW}antennaTypes.json{colorama.Fore.RESET}")
    else:
        for ap in esx_aps:
            for slot, config in ap.slots.items():
                try:
                    ap.slots[slot]["antennatype"] = next((item["name"] for item in antennas["antennaTypes"] if item["id"] == config["antennaid"]), "NA")
                except KeyError:
                    ap.slots[slot]["antennatype"] = "NULL"
                    print(f"{status.info}Antenna does not have name, setting to NULL")

    
def freq_to_channel(freq):

    if freq in range(2412, 2485): #2.4GHz
        return int((freq - 2405) / 5)
    elif freq in range(5180, 5886): #5GHz
        return int((freq / 5) - 1000)
    elif freq in range(5955, 7116): #6GHz
        return int(((freq - 5955) / 5) + 1)
    

def read_measured_radios(esx_aps, json_path):

    try:
        with open(os.path.join(json_path, "measuredRadios.json"), "r") as f:
            measured = json.load(f)

    except FileNotFoundError:
        print(f"{status.info}Not found: {colorama.Fore.YELLOW}measuredRadios.json{colorama.Fore.RESET}")
    else:
        for radio in measured["measuredRadios"]:
            for ap in esx_aps:
                if radio["accessPointId"] == ap.id:
                    ap.measuredradio = radio["accessPointMeasurementIds"][0] #Save first found measurement id


def read_access_point_measurements(esx_aps, json_path):

    try:
        with open(os.path.join(json_path, "accessPointMeasurements.json"), "r") as f:
            measurements = json.load(f)

    except FileNotFoundError:
        print(f"{status.info}Not found: {colorama.Fore.YELLOW}accessPointMeasurements.json{colorama.Fore.RESET}")
    else:
        for measurement in measurements["accessPointMeasurements"]:
            for ap in esx_aps:
                if measurement["id"] == ap.measuredradio:
                    try:
                        ap.ssid = measurement["ssid"]
                    except KeyError:
                        ap.ssid = "" #Replace with blank SSID if measurement has no SSID
                    ap.mac = measurement["mac"]
                    ap.ekahau = "Measured"





