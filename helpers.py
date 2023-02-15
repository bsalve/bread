from riotwatcher import LolWatcher

watcher = LolWatcher("RGAPI-02309ce1-eefc-4b17-ae91-e7973f332d50")
region = "na1"

champ_dict = {}
ss_dict = {}

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
def get_match_stats(match_number, match_list, region):

    match_detail = watcher.match.by_id(region, match_list[match_number])

    match = {}

    match["metadata"] = []
    match["info"] = []

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

        participant["item_list"] = []
        for i in range(7):
            participant["item_list"].append(row["item"+str(i)])

        match["info"].append(participant)

    for row in match["info"]:

        row["champion"] = champ_dict[str(row["champion"])]

        row["ss1"] = ss_dict[str(row["ss1"])]
        row["ss2"] = ss_dict[str(row["ss2"])]

    return match