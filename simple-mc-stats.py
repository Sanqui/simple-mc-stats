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

ITEM_STAT_NAMES = 'stat.mineBlock stat.useItem stat.craftItem'.split()

if os.path.isfile("name_cache.json"):
    name_cache = json.load(open("name_cache.json"))
else:
    name_cache = {}

stats_per_player = {}
players_per_stat = defaultdict(Counter)

global_stats = Counter()
for stat in ITEM_STAT_NAMES:
    global_stats[stat] = Counter()

for filename in os.listdir(STATS_DIR):
    j = json.load(open(STATS_DIR+filename))
    uuid = filename.split('.')[0].replace('-', '')
    if uuid not in name_cache:
        name_cache[uuid] = requests.get('https://api.mojang.com/user/profiles/'+uuid+'/names').json()[0]['name']
    name = name_cache[uuid]
    stats_per_player[name] = Counter(j)
    for stat in ITEM_STAT_NAMES:
        stats_per_player[name][stat] = Counter()
    
    for field, value in j.items():
        players_per_stat[field][name] = value
        for stat in ITEM_STAT_NAMES:
            if field.startswith(stat):
                players_per_stat[stat][name] += value
                stats_per_player[name][stat][field.split('.')[-1]] = value
                global_stats[stat][field.split('.')[-1]] += value
    #global_stats.update(j) # TODO remove achievement progress

json.dump(name_cache, open('name_cache.json', 'w'))

output = Template(filename="templates/index.html").render(
    stats_per_player=stats_per_player,
    players_per_stat=players_per_stat,
    global_stats=global_stats,
    server_name=SERVER_NAME)
open(OUTPUT_PATH+'index.html', 'w').write(output)

#print(players_per_stat['stat.mineBlock'].most_common(50))
