import os
import json
import shutil

import colorama

from messageLib import *


def rescale_maps(floors, map_floors, aps, old_esx_path, new_esx_path):

    update_maps = {}
    for floor in floors:
        if floor.name in [m.name for m in map_floors]:
            update_maps[floor.name] = {}

    for update_map in update_maps.keys():
        old_floor_index = next(index for index, floor in enumerate(floors) if floor.name == update_map)
        update_maps[update_map]["old_id"] = floors[old_floor_index].id
        update_maps[update_map]["old_image"] = floors[old_floor_index].image
        update_maps[update_map]["old_width"] = floors[old_floor_index].width
        update_maps[update_map]["old_height"] = floors[old_floor_index].height
        new_floor_index = next(index for index, floor in enumerate(map_floors) if floor.name == update_map)
        update_maps[update_map]["new_id"] = map_floors[new_floor_index].id
        update_maps[update_map]["new_image"] = map_floors[new_floor_index].image
        update_maps[update_map]["new_width"] = map_floors[new_floor_index].width
        update_maps[update_map]["new_height"] = map_floors[new_floor_index].height
        update_maps[update_map]["reference"] = map_floors[new_floor_index].points
        update_maps[update_map]["scaling"] = map_floors[new_floor_index].scaling

    update_aps = {}
    for ap in aps:
        if ap.location_name in update_maps.keys():
            if ap.location_x != "" and ap.location_y != "":

                old_floor_index = next(index for index, floor in enumerate(floors) if floor.name == ap.location_name)
                old_width = floors[old_floor_index].width
                old_height = floors[old_floor_index].height
                old_coords = sorted(floors[old_floor_index].points, key=lambda x: x[0]) #Sort points by lowest X value
                old_x1 = old_coords[0][0]
                old_y1 = old_coords[0][1]
                old_x2 = old_coords[1][0]
                old_y2 = old_coords[1][1]
                
                new_floor_index = next(index for index, floor in enumerate(map_floors) if floor.name == ap.location_name)
                new_width = map_floors[new_floor_index].width
                new_height = map_floors[new_floor_index].height
                new_coords = sorted(map_floors[new_floor_index].points, key=lambda x: x[0]) #Sort points by lowest X value
                new_x1 = new_coords[0][0]
                new_y1 = new_coords[0][1]
                new_x2 = new_coords[1][0]
                new_y2 = new_coords[1][1]

                new_zero_x_offset = new_x1 - (new_width * old_x1 / old_width)
                new_zero_y_offset = new_y1 - (new_height * old_y1 / old_height)

                new_ap_x = (ap.location_x / (old_x2 - old_x1) * (new_x2 - new_x1)) + new_zero_x_offset
                new_ap_y = (ap.location_y / (old_y2 - old_y1) * (new_y2 - new_y1)) + new_zero_y_offset

                update_aps[ap.name] = {}
                update_aps[ap.name]["new_ap_x"] = round(new_ap_x)
                update_aps[ap.name]["new_ap_y"] = round(new_ap_y)

    #accessPoints.json
    with open(os.path.join(old_esx_path, "accessPoints.json"), "r") as f:
        ap_json = json.load(f)

    for ap in ap_json["accessPoints"]:
        if ap["name"] in update_aps.keys():
            ap_json["accessPoints"][ap_json["accessPoints"].index(ap)]["location"]["coord"].update({"x": update_aps[ap["name"]]["new_ap_x"]})
            ap_json["accessPoints"][ap_json["accessPoints"].index(ap)]["location"]["coord"].update({"y": update_aps[ap["name"]]["new_ap_y"]})
    
    with open(os.path.join(old_esx_path, "accessPoints.json"), "w") as f:
        json.dump(ap_json, f, indent=2)
    
    #floorPlans.json
    with open(os.path.join(old_esx_path, "floorPlans.json"), "r") as f:
        floor_json = json.load(f)

    for floor in floor_json["floorPlans"]:
        if floor["name"] in update_maps.keys():
            floor_json["floorPlans"][floor_json["floorPlans"].index(floor)].update({"width": update_maps[floor["name"]]["new_width"]})
            floor_json["floorPlans"][floor_json["floorPlans"].index(floor)].update({"height": update_maps[floor["name"]]["new_height"]})
            floor_json["floorPlans"][floor_json["floorPlans"].index(floor)].update({"cropMaxX": update_maps[floor["name"]]["new_width"]})
            floor_json["floorPlans"][floor_json["floorPlans"].index(floor)].update({"cropMaxY": update_maps[floor["name"]]["new_height"]})
            floor_json["floorPlans"][floor_json["floorPlans"].index(floor)].update({"metersPerUnit": update_maps[floor["name"]]["scaling"]})

    with open(os.path.join(old_esx_path, "floorPlans.json"), "w") as f:
        floor_json = json.dump(floor_json, f, indent=2)
 
    #Remove reference points & change images
    os.remove(os.path.join(old_esx_path, f'referencePoints.json'))
    for map_name, map_data in update_maps.items():
        os.remove(os.path.join(old_esx_path, f'image-{map_data["old_image"]}'))
        shutil.copy(os.path.join(new_esx_path, f'image-{map_data["new_image"]}'), 
                    os.path.join(old_esx_path, f'image-{map_data["old_image"]}'))
    
    #Debug
    #print(json.dumps(update_aps, indent=4))
    #print(json.dumps(update_maps, indent=4))




