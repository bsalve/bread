from flask import Flask, redirect, render_template, request, make_response, jsonify
from riotwatcher import ApiError
import time

from helpers import get_ranked_stats, get_match_stats, update_static_data, watcher, region

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

matches = []
quantity = 5
posts = 20

@app.route("/")
def index():

    update_static_data(region)

    return render_template("index.html")

@app.route("/profile")
def profile():

    global matches

    matches.clear()

    query = request.args.get("search")

    if not query:

        return redirect(request.referrer)

    try: 

        summoner = watcher.summoner.by_name(region, query)

    except ApiError as err:

        error_code = err.response.status_code

        if error_code == 403:

            return render_template("error.html", error_message = "Refused Access (Invalid API key)", error_code = error_code)

        elif error_code == 404: 

            return render_template("error.html", error_message = "Summoner not found.", error_code = error_code)
        
        elif error_code == 429: 

            return render_template("error.html", error_message = "Too many requests. Try again later.", error_code = error_code)

        else: 

            raise

    ranked_stats = watcher.league.by_summoner(region, summoner["id"])

    soloq = "Unranked"
    flexq = "Unranked"

    for queue_type in range(len(ranked_stats)):

        if ranked_stats[queue_type]["queueType"] == "RANKED_SOLO_5x5":

            soloq = get_ranked_stats(queue_type, ranked_stats)
        
        elif ranked_stats[queue_type]["queueType"] == "RANKED_FLEX_SR":

            flexq = get_ranked_stats(queue_type, ranked_stats)

    match_list = watcher.match.matchlist_by_puuid(region, summoner["puuid"])

    for i in range(posts):

        matches.append(get_match_stats(i, match_list, region))

    return render_template("profile.html", summoner = summoner, soloq = soloq, flexq = flexq, matches = matches)

@app.route("/load")
def load():

    time.sleep(0.2)

    if request.args:

        counter = int(request.args.get("c"))

        if counter == 0:
            
            print(f"Returning posts 0 to {quantity}")

            res = make_response(jsonify(matches[0: quantity]), 200)

        elif counter == posts:

            print("No more posts")

            res = make_response(jsonify({}), 200)

        else:

            print(f"Returning posts {counter} to {counter + quantity}")

            res = make_response(jsonify(matches[counter: counter + quantity]), 200)

    return res