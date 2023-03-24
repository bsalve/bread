from riotwatcher import LolWatcher
import time
import datetime

watcher = LolWatcher("RGAPI-4c0eb074-56ea-4a0f-9631-450a65b7970f")
region = "na1"

champ_dict = {}
ss_dict = {}

# queueIDs from https://static.developer.riotgames.com/docs/lol/queues.json

queueIds = {0: "Custom", 
            400: "Draft",
            420: "Solo/Duo", 
            430: "Blind",
            440: "Flex",
            450: "ARAM",
            700: "Clash",
            720: "ARAM Clash",
            830: "Intro Bot",
            840: "Beginner Bot",
            850: "Intermediate Bot",
            900: "ARURF",
            1400: "Ultimate Spellbook",
            1900: "URF",
            2000: "Tutorial 1",
            2010: "Tutorial 2",
            2020: "Tutorial 3"}

# Updates champion dictionary and summoner spell dictionaries with live data
def update_static_data(region):

    latest = watcher.data_dragon.versions_for_region(region)["n"]["champion"]

    static_champ_list = watcher.data_dragon.champions(latest, False, "en_US")

    for key in static_champ_list["data"]:

        row = static_champ_list["data"][key]

        champ_dict[row["key"]] = row["id"]

    static_ss_list = watcher.data_dragon.summoner_spells(latest, False)

    for key in static_ss_list["data"]:

        row = static_ss_list["data"][key]

        ss_dict[row["key"]] = row["id"]

# Converts seconds to minutes and seconds (returns string with minutes and seconds)
def seconds_converter(seconds):

    return time.strftime("%H:%M:%S", time.gmtime(seconds))

# Returns a dictionary of ranked stats, takes in queue_type and summoner parameters
def get_ranked_stats(queue_type, summoner):

    ranked_stats = {}

    ranked_stats["tier"] = str(summoner[queue_type]["tier"])
    ranked_stats["rank"] = str(summoner[queue_type]["rank"])
    ranked_stats["lp"] = str(summoner[queue_type]["leaguePoints"])

    wins = str(summoner[queue_type]["wins"])
    losses = str(summoner[queue_type]["losses"])
    
    ranked_stats["wins"] = wins
    ranked_stats["losses"] = losses
    ranked_stats["winrate"] = str(round((float(wins)/float(int(wins)+int(losses))*100))) + "%"

    return ranked_stats

# Returns a dictionary of "metadata" and "info", with information on participants, runes, champs, etc.
def get_match_stats(summoner, match_number, match_list, region):

    match = {}

    try: 
        
        match_detail = watcher.match.by_id(region, match_list[match_number])

    except IndexError: 

        return match

    match["metadata"] = []
    match["info"] = []

    # Metadata (summoner win/loss, game duration, game timestamp)
    metadata = {}

    metadata["gameMode"] = queueIds[int(match_detail["info"]["queueId"])]
    metadata["duration"] = seconds_converter(match_detail["info"]["gameDuration"])
    metadata["timestamp"] = datetime.datetime.fromtimestamp(match_detail["info"]["gameStartTimestamp"]/1000).strftime("%m/%d/%y")

    # Match info (name, champ, summoner spells, kda, etc.)
    for row in match_detail["info"]["participants"]:

        participant = {}

        participant["name"] = row["summonerName"]
        participant["champion"] = row["championId"]
        participant["ss1"] = row["summoner1Id"]
        participant["ss2"] = row["summoner2Id"]
        participant["role"] = row["teamPosition"]
        participant["kills"] = row["kills"]
        participant["deaths"] = row["deaths"]
        participant["assists"] = row["assists"]
        participant["win"] = row["win"]
        participant["cs"] = row["totalMinionsKilled"]
        participant["visionScore"] = row["visionScore"]
        participant["damage"] = row["totalDamageDealtToChampions"]
        participant["goldEarned"] = row["goldEarned"]
        participant["champLevel"] = row["champLevel"]

        if summoner["name"] == row["summonerName"]:

            if participant["win"] == True:

                metadata["result"] = "VICTORY"

            else:

                metadata["result"] = "DEFEAT"

        participant["item_list"] = []
        for i in range(7):

            participant["item_list"].append(row["item"+str(i)])

        match["info"].append(participant)

    for row in match["info"]:

        row["champion"] = champ_dict[str(row["champion"])]

        row["ss1"] = ss_dict[str(row["ss1"])]
        row["ss2"] = ss_dict[str(row["ss2"])]

    match["metadata"].append(metadata)

    return match