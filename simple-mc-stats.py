#!/usr/bin/python3
import os
import os.path
import json
from collections import Counter, defaultdict

import requests
from mako.template import Template

STATS_DIR = "stats/"
OUTPUT_PATH = "out/"
SERVER_NAME = "Minecraft server"

ITEM_STAT_NAMES = 'mined used crafted'.split()

if os.path.isfile("name_cache.json"):
    name_cache = json.load(open("name_cache.json"))
else:
    name_cache = {}

stats_per_player = defaultdict(lambda: defaultdict(Counter))
players_per_stat = defaultdict(Counter)

global_stats = defaultdict(Counter)

for filename in os.listdir(STATS_DIR):
    j = json.load(open(STATS_DIR+filename))
    uuid = filename.split('.')[0].replace('-', '')
    if uuid not in name_cache:
        name_cache[uuid] = requests.get('https://api.mojang.com/user/profiles/'+uuid+'/names').json()[0]['name']
    name = name_cache[uuid]

    for field, value in j['stats'].items():
        if not field.startswith("minecraft:"):
            continue
        stat = field.split(":")[-1]

        #print(stat)

        for item, value in value.items():
            if not item.startswith("minecraft:"):
                continue
            item = item.split(":")[-1]
            if stat == 'custom':
                players_per_stat[item][name] += value
            else:
                players_per_stat[stat][name] += value
            stats_per_player[name][stat][item] = value
            global_stats[stat][item] += value

json.dump(name_cache, open('name_cache.json', 'w'))

output = Template(filename="templates/index.html").render(
    stats_per_player=stats_per_player,
    players_per_stat=players_per_stat,
    global_stats=global_stats,
    server_name=SERVER_NAME)
open(OUTPUT_PATH+'index.html', 'w').write(output)
