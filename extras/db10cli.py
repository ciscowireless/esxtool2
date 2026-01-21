'''
Usage:
db10cli.py <show_ap_summary.txt> <esxtool_db10.csv>

'''
import sys
import csv
import re

from datetime import datetime

SLOT1_ENABLED_COLUMN = 19
SLOT2_ENABLED_COLUMN = 27
SLOT3_ENABLED_COLUMN = 35
SLOT1_CHANNEL_COLUMN = 20
SLOT2_CHANNEL_COLUMN = 28
SLOT3_CHANNEL_COLUMN = 36
DB10_BEAMWIDTH_COLUMN = 7

RF_TAG_MAP = {
    "Boresight" : "RF_TAG_DB10_NARROW",
    "Wide" : "RF_TAG_DB10_WIDE"
}

def generate_cli(csv_file):

    ap_count = 0
    cli_1, cli_2 = [], []
    with open(csv_file, "r") as c:
        csv_read = csv.reader(c)
        for row in csv_read:
            if row[0] == "AP Name": continue   
            ap_name = row[0]
            ap_count += 1
            #if ap_name in ap_mac_map.keys():

            beam_mode = re.search(r"Wireless\sCW9179F\s\(Wide\)|Wireless\sCW9179F", row[DB10_BEAMWIDTH_COLUMN])
            match beam_mode.group(0):
                case "Wireless CW9179F":
                    cli_1.append(f"ap {ap_name} \n rf-tag {RF_TAG_MAP["Boresight"]}\n")
                case "Wireless CW9179F (Wide)":
                    cli_1.append(f"ap {ap_name} \n rf-tag {RF_TAG_MAP["Wide"]}\n")
            
            slot1_enabled = bool(row[SLOT1_ENABLED_COLUMN])
            slot1_channel = row[SLOT1_CHANNEL_COLUMN]
            slot2_enabled = bool(row[SLOT2_ENABLED_COLUMN])
            slot2_channel = row[SLOT2_CHANNEL_COLUMN]
            slot3_enabled = bool([SLOT3_ENABLED_COLUMN])
            slot3_channel = row[SLOT3_CHANNEL_COLUMN]

            if slot1_enabled:
                cli_2.append(f"ap name {ap_name} slot 1 shutdown \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 1 radio role manual client-serving \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 1 channel auto \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 1 txpower auto \n")
                cli_2.append(f"ap name {ap_name} no slot 1 shutdown \n")
            elif not slot1_enabled:
                cli_2.append(f"ap name {ap_name} slot 1 shutdown \n")

            if slot2_enabled:
                cli_2.append(f"ap name {ap_name} slot 2 shutdown \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 2 radio role manual client-serving \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 2 channel auto \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 2 txpower auto \n")
                cli_2.append(f"ap name {ap_name} no slot 2 shutdown \n")
            elif not slot2_enabled:
                cli_2.append(f"ap name {ap_name} slot 2 shutdown \n")

            if slot3_enabled:
                cli_2.append(f"ap name {ap_name} slot 3 shutdown \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 3 radio role manual client-serving \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 3 channel {slot3_channel} \n")
                cli_2.append(f"ap name {ap_name} dot11 5ghz slot 3 txpower auto \n")
                cli_2.append(f"ap name {ap_name} no slot 3 shutdown \n")
            elif not slot3_enabled:
                cli_2.append(f"ap name {ap_name} slot 3 shutdown \n")
        
        print(f"Processed: {ap_count} APs")
    return cli_1, cli_2


def save_cli(cli_1, cli_2):

    with open("wlc-cli-db10.txt", "w") as t:
        t.write(str(datetime.now())[:-7])
        t.write(f"\n\n===== AP RT Tag Config =====\n\n")
        for line in cli_1: t.write(line)
        t.write(f"\n\n===== AP Slot Config =====\n\n")
        for line in cli_2: t.write(line)


if __name__ == "__main__":

    #show_ap_summary, esxtool_csv = sys.argv[1], sys.argv[2]
    #ap_mac = map_ap_mac(show_ap_summary)
    esxtool_csv = sys.argv[1]
    cli_1, cli_2 = generate_cli(esxtool_csv)
    save_cli(cli_1, cli_2)