'''
Usage:
m4cli.py <show_ap_summary.txt> <esxtool_9104.csv>

'''
import sys
import csv
import re

RF_TAG_MAP = {
    "Slot1Narrow_Slot2Narrow" : "RFT_Narrow",
    "Slot1Narrow10_Slot2Narrow10" : "RFT_Narrow10",
    "Slot1Narrow20_Slot2Narrow20" : "RFT_Narrow20",
    "Slot1Wide_Slot2Wide" : "RFT_Wide"
}

SLOT1_ENABLED_ROW = 19
SLOT1_ANTENNA_ROW = 25
SLOT2_ENABLED_ROW = 27
SLOT2_ANTENNA_ROW = 33

def map_ap_mac(text_file):

    ap_mac_dict = {}
    with open(text_file, "r") as t:
        for line in t.readlines():
            if not line.startswith("AP Name"):
                ap = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
                try:
                    ap_name, ap_mac = ap.group(1), ap.group(4)
                except AttributeError:
                    continue
                else:
                    ap_mac_dict.update({ap_name: ap_mac})

    return ap_mac_dict


def generate_cli(csv_file, ap_mac_map):

    cli_1, cli_2 = [], []
    with open(csv_file, "r") as c:
        csv_read = csv.reader(c)
        for row in csv_read:
            if row[0] == "AP Name": continue      
            ap_name = row[0]
            #if ap_name in ap_mac_map.keys():
            slot1_enabled = row[SLOT1_ENABLED_ROW].upper()
            slot1_antenna = row[SLOT1_ANTENNA_ROW]
            slot2_enabled = row[SLOT2_ENABLED_ROW].upper()
            slot2_antenna = row[SLOT2_ANTENNA_ROW]
            slot1_enabled = True if slot1_enabled == "TRUE" else not slot1_enabled
            slot2_enabled = True if slot2_enabled == "TRUE" else not slot2_enabled
            slot1_mode = re.search(r"Wide|Narrow\s|Narrow\_10|Narrow\_20", slot1_antenna)
            slot2_mode = re.search(r"Wide|Narrow\s|Narrow\_10|Narrow\_20", slot2_antenna)
            rft = ""
            match slot1_mode.group(0):
                case "Narrow ":
                    rft += "Slot1Narrow_"
                case "Narrow_10":
                    rft += "Slot1Narrow10_"
                case "Narrow_20":
                    rft += "Slot1Narrow20_"
                case "Wide":
                    rft += "Slot1Wide_"
                case _:
                    rft += "Null"

            match slot2_mode.group(0):
                case "Narrow ":
                    rft += "Slot2Narrow"
                case "Narrow_10":
                    rft += "Slot2Narrow10"
                case "Narrow_20":
                    rft += "Slot2Narrow20"
                case "Wide":
                    rft += "Slot2Wide"
                case _:
                    rft += "Null"

            #cli = f"ap {ap_mac_map[ap_name]} \n rf-tag {RF_TAG_MAP[rft]}"
            cli_1.append(f"ap {ap_name} \n rf-tag {RF_TAG_MAP[rft]}\n")
            if not slot1_enabled: cli_2.append(f"ap name {ap_name} slot 1 shutdown \n")
            if not slot2_enabled: cli_2.append(f"ap name {ap_name} slot 2 shutdown \n")

    return cli_1, cli_2


def save_cli(cli_1, cli_2):

    with open("wlc-cli.txt", "w") as t:
        t.write("===== RFT commands =====\n\n")
        for line in cli_1:
            t.write(line)
        t.write("\n\n===== Slot commands =====\n\n")
        for line in cli_2:
            t.write(line)
    
    print(f"{len(cli_1)} RFT configs\n{len(cli_2)} Slot configs")


if __name__ == "__main__":

    show_ap_summary, esxtool_csv = sys.argv[1], sys.argv[2]
    ap_mac = map_ap_mac(show_ap_summary)
    cli_1, cli_2 = generate_cli(esxtool_csv, ap_mac)
    save_cli(cli_1, cli_2)