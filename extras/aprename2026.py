'''
AP rename sript to create CSV containing standard AP names as per CL naming convention, part of a larger process, of no use in isolation
'''
import csv
import sys

all_models = [
            "AP1562I",
            "AP2800E",
            "AP2800I",
            "AP3700E",
            "AP3700I",
            "AP9120E",
            "AP9120I",
            "AP9124D",
            "AP9124I",
            "AP9130E",
            "AP9130I",
            "AP9166I",
            "Catalyst 9166 with Dual 5 GHz",
            "Catalyst 9166",
            "Catalyst 9166D1",
            "Catalyst IW9167I",
            "Wireless CW9176I",
            "Wireless CW9176D1",
            "Wireless CW9178I",
            "CW9172H",
            "Wireless CW9179F (Boresight)",
            "Wireless CW9179F (Wide)"
            ]

internal_omni = [
            "AP1562I",
            "AP2800I",
            "AP3700I",
            "AP9120I",
            "AP9124I",
            "AP9130I",
            "AP9166I",
            "Catalyst 9166 with Dual 5 GHz",
            "Catalyst 9166",
            "Catalyst IW9167I",
            "Wireless CW9176I",
            "Wireless CW9178I",
            "CW9172H",
            ]

internal_directional = [
            "AP9124D",
            "Catalyst 9166D1",
            "Wireless CW9176D1"
            ]

antennas = {
            "2513" : "G", #Gilaroo
            "2566D" : "T", #Trout
            "2566P" : "P", #Patch
            "2524" : "O", #Omni
            "2535" : "O", #Omni
            "9104" : "4", 
            "9103" : "3",
            "9102" : "2",
            "9101" : "1",
            "9179F": "F",
            "unknown" : "U", #Unknown external antenna
            "mixed" : "X", #Multiple different external antennas
            "internal" : "I", #Internal omni
            "directional" : "D" #Internal directional
            }

maps = {
        "Auditorium_L0" : "AUDL0",
        "Auditorium_L1" : "AUDL1",
        "Congress_L0_Europe-Foyer" : "CONL0",
        "Congress_L0_Jade-Lounge" : "CONL0",
        "Congress_L1_Rooms-G" : "CONL1",
        "Elicium_B1" : "ELCB1",
        "Elicium_L0" : "ELCL0",
        "Elicium_L1" : "ELCL1",
        "Elicium_L2" : "ELCL2",
        "Elicium_L3" : "ELCL3",
        "Elicium_L4" : "ELCL4",
        "Elicium_L5" : "ELCL5",
        "Entrance-K_L0" : "ENKL0",
        "Entrance-K_L0_Tent" : "ENKL0",
        "Entrance-K_L1" : "ENKL1",
        "Hal-1_L0" : "H01L0",
        "Hal-1_L1" : "H01L1",
        "Hal-2_L0" : "H02L0",
        "Hal-3_L0" : "H03L0",
        "Hal-4_L0_Amtrium" : "H04L0",
        "Hal-4_L1_Amtrium" : "H04L1",
        "Hal-5_L0" : "H05L0",
        "Hal-6_L0" : "H06L0",
        "Hal-7_L0" : "H07L0",
        "Hal-8_L1" : "H08L1",
        "Hal-9_L1" : "H09L1",
        "Hal-10_L1" : "H10L1",
        "Hal-11_L1" : "H11L1",
        "Hal-12_L1" : "H12L1",
        "Hal-12_L1_Keynote" : "H12L1",
        "Holland_L0" : "HOLL0",
        "Holland_L1" : "HOLL1",
        "Holland_L2_Restaurant" : "HOLL2",
        "Holland_L2_Rooms-C" : "HOLL2",
        "Passage_L1_H8H10" : "PASL1",
        "Passage_L1_H7H8" : "PASL1",
        "Strandzuid_L0" : "STRL0"
        }

csv_data = []

#Column numbers
OLD_AP_NAME = 0
FLOOR = 1
MODEL = 7
HEIGHT = 14
ANTENNA_1 = 17
ANTENNA_2 = 25
ANTENNA_3 = 33
ANTENNA_4 = 41


def do_rename(input_file, output_file = "new-names.csv"):

    with open(input_file) as input_csv:
        reader = csv.reader(input_csv)
        for row in reader:
            csv_data.append(row)

    with open(output_file, 'w', newline='') as output_csv:
        writer = csv.writer(output_csv)
        row_count = 0
        for row in csv_data:
            row_count += 1
            if row_count == 1: continue #Skip 1st row (headings)
            
            old_ap_name = row[OLD_AP_NAME]
            ap_model = row[MODEL]
            #print(ap_model)
            try:
                location = maps[row[FLOOR]]
            except KeyError:
                location = "X00XX" #Non-CL location
            
            height = float(row[HEIGHT])
            if height <= 3:
                height = "L"
            elif height >= 10:
                height = "H"
            else:
                height = "M"   

            if ap_model in internal_directional:
                antenna = antennas["directional"]
                ap_antennas = ""
            elif ap_model in internal_omni:
                antenna = antennas["internal"]
                ap_antennas = ""
            else:
                ap_antennas = []
                for antenna_id in (ANTENNA_1, ANTENNA_2, ANTENNA_3, ANTENNA_4):
                    for antenna_model in antennas.keys():
                        try:
                            if antenna_model in row[antenna_id]:
                                ap_antennas.append(antenna_model)
                        except IndexError:
                            pass
                    
                    if len(ap_antennas) == 0:
                        ap_antennas.append("unknown")

                if len(set(ap_antennas)) > 1: #Set cannot have duplicates, len 1 signifies all antennas are the same
                    antenna = antennas["mixed"]
                else:
                    antenna = antennas[list(set(ap_antennas))[0]] #Set of length 0 means all antennas match, take first item

            new_ap_name = f"{location}-{antenna}{height}-"

            print(f"{location} {old_ap_name} {ap_antennas} {ap_model} {height} {new_ap_name}")
            
            data = [old_ap_name, new_ap_name, row[FLOOR], ap_antennas, ap_model]
            writer.writerow(data)


if __name__ == "__main__":

    do_rename(sys.argv[1])

