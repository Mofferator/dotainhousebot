import urllib3, json

http = urllib3.PoolManager()

def getplayermmr(steamid):
    p = http.request("GET", "https://api.opendota.com/api/players/" + str(steamid))
    player = json.loads(p.data)
    mmr = player["rank_tier"]
    if mmr is None:
        return 3500
    print(mmr)
    realmmr = mmr * 67
    return realmmr

if __name__ == "__main__":
    print(getplayermmr(108305168))