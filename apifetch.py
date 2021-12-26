import urllib3, json, os
from dotenv import load_dotenv

load_dotenv('.env')
KEY = os.getenv("OPENDOTAKEY")

http = urllib3.PoolManager()

def getplayermmr(steamid):
    p = http.request("GET", "https://api.opendota.com/api/players/" + str(steamid) + "?api_key=" + str(KEY))
    player = json.loads(p.data)
    mmr = player["rank_tier"]
    if mmr is None:
        return 3500
    realmmr = mmr * 67
    return realmmr

def getmatchidlist(leagueid):
    if __name__ == "__main__":
        print("fetching match records...\n")
    #ml = http.request("GET", "https://api.stratz.com/api/v1/league/" + leagueid + "/matches?include=Player&take=250")
    resp = http.request(
    "GET",
    "https://api.stratz.com/api/v1/league/{}/matches?include=Player&take=250".format(leagueid),
    headers={
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJodHRwczovL3N0ZWFtY29tbXVuaXR5LmNvbS9vcGVuaWQvaWQvNzY1NjExOTgwNjg1NzA4OTYiLCJ1bmlxdWVfbmFtZSI6IkhhcHB5IE51dCIsIlN1YmplY3QiOiJkYjZjYjM1MC02ZTkzLTQ5YjEtOGQzOS1lMjU5Yzk3OGVlYjEiLCJTdGVhbUlkIjoiMTA4MzA1MTY4IiwibmJmIjoxNjM5MTYzMzUwLCJleHAiOjE2NzA2OTkzNTAsImlhdCI6MTYzOTE2MzM1MCwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.zWPQhM0b2-WfmUb1x14gl0fXRGszDSQUXbHqCNfdYRs"
    }
    )
    idList = []
    matchlist = json.loads(resp.data)
    for match in matchlist:
        idList.append(match['id'])
    return idList

#for a given match, get the list of players and the winning team
def getMatchInfo(matchId):
    m = http.request("GET", "https://api.opendota.com/api/matches/" + str(matchId) + "/?api_key=" + str(KEY))
    match = json.loads(m.data)
    listOfPlayers = []
    if "match_id" in match:
        matchId = match["match_id"]
        if match["radiant_win"] == "true":
            winner = 1
        else:
            winner = 0
        for x in match["players"]:
            listOfPlayers.append(x["account_id"])
        return (matchId, winner, listOfPlayers)
    else:
        return 0

if __name__ == "__main__":
    testId = 108305168
    print(getplayermmr(testId))
    print(getmatchidlist(11595))
    print(getMatchInfo(6342943242))