#!/usr/bin/python

import sys
import os
sys.path.append(os.getcwd())

def add_monster(id, name):
    try:
        from monsters import monsters_name_map as imported_map
        if len(imported_map) > 0:
            name_map = imported_map
    except:
        print "Can't find monsters.py"
        sys.exit(-2)

    name_map[id] = name

    all_monsters = []
    for mon in name_map.keys():
        all_monsters.append(str(mon)[0:3])

    all_monsters = list(set(all_monsters))
    all_monsters.sort()
    if "143" in all_monsters:
        all_monsters.remove("143") # Rainbowmon
    if "151" in all_monsters:
        all_monsters.remove("151") # Devilmon

    with open("monsters.py", "w") as f:
        f.write("monsters_name_map = {\n")
        for mon in all_monsters:
            base = mon
            water = mon + "11"
            fire = mon + "12"
            wind = mon + "13"
            light = mon + "14"
            dark = mon + "15"
            f.write("    \"%s\": \"%s\",\n" % (base, name_map.get(base, "")))
            f.write("    \"%s\": \"%s\",\n" % (water, name_map.get(water, "")))
            f.write("    \"%s\": \"%s\",\n" % (fire, name_map.get(fire, "")))
            f.write("    \"%s\": \"%s\",\n" % (wind, name_map.get(wind, "")))
            f.write("    \"%s\": \"%s\",\n" % (light, name_map.get(light, "")))
            f.write("    \"%s\": \"%s\",\n" % (dark, name_map.get(dark, "")))
            f.write("\n")
        f.write("    \"15105\": \"Devilmon\",\n")
        f.write("    \"14314\": \"Rainbowmon\"\n")
        f.write("}\n")

    try:
        os.remove("monsters.pyc")
    except:
        pass
    try:
        os.remove("monsters.pyo")
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s id name\n" % sys.argv[0]
        sys.exit(-1)
    add_monster(sys.argv[1], sys.argv[2])
