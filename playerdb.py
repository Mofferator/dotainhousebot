import sqlite3

conn = sqlite3.connect('players.db')

c = conn.cursor()

def addGuildTable(guild_id):
    gid = "guild" + str(guild_id)
    settingsId = "settings" + str(guild_id)
    matchesId = "matches" + str(guild_id)
    c.execute("CREATE TABLE IF NOT EXISTS {} (user_id integer, member text, steam_id integer, mmr_overide integer)".format(gid))
    c.execute("CREATE TABLE IF NOT EXISTS {} (leagueId integer, currentJoinId integer, currentJoinTime integer, role text, adminrole text, resultsChannel integer)".format(settingsId))
    c.execute("""
    CREATE TABLE IF NOT EXISTS {}
    (matchId integer,
    winner integer,
    player0 integer,
    player1 integer,
    player2 integer,
    player3 integer,
    player4 integer,
    player5 integer,
    player6 integer,
    player7 integer,
    player8 integer,
    player9 integer)
    """.format(matchesId))
    c.execute("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?)".format(settingsId), (0, 0, 0, "", "", 0))
    conn.commit()

def addPlayer(user_id, steam_id, member, guild_id):
    gid = "guild" + str(guild_id)
    c.execute("SELECT * FROM {} WHERE user_id = ?".format(gid), (user_id,))
    if c.fetchall() == []:
        c.execute("INSERT INTO {} VALUES (?, ?, ?, 0)".format(gid), (user_id, member, steam_id))
        conn.commit()
        return "Player {} added to database".format(member)
    else:
        return "Player {} already in database".format(member)

def removePlayer(user_id, guild_id, member):
    gid = "guild" + str(guild_id)
    c.execute("DELETE FROM {} WHERE user_id = ?".format(gid), (user_id,))
    conn.commit()
    return "Player {} removed from database".format(member)

def getPlayer(user_id, guild_id):
    gid = "guild" + str(guild_id)
    c.execute("SELECT * FROM {} WHERE user_id = ?".format(gid), (user_id,))
    return c.fetchall()

def changeSetting(guild_id, setting, value):
    settingsId = "settings" + str(guild_id)
    c.execute("UPDATE {} SET {} = ?".format(settingsId, setting), (value,))
    conn.commit()

def getSetting(guild_id, setting):
    settingsId = "settings" + str(guild_id)
    c.execute("SELECT {} FROM {}".format(setting, settingsId))
    return c.fetchall()[0][0]

def getMMROveride(guild_id, user_id):
    player = getPlayer(user_id, guild_id)[0]
    return player[3]

def getListOfMatchIds(guild_id):
    matchesId = "matches" + str(guild_id)
    c.execute("SELECT * FROM {}".format(matchesId))
    ListOfMatches = c.fetchall()
    ListOfMatchIds = []
    for match in ListOfMatches:
        ListOfMatchIds.append(match[0])
    return ListOfMatchIds



def addMatch(guild_id, matchId, winner, LoP):
    if matchId not in getListOfMatchIds(guild_id):
        matchesId = "matches" + str(guild_id)
        c.execute("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(matchesId), 
            (matchId, winner, LoP[0], LoP[1], LoP[2], LoP[3], LoP[4], LoP[5], LoP[6], LoP[7], LoP[8], LoP[9]))
        conn.commit()
    else:
        print("Match already recorded")

if __name__ == "__main__":
    from player import Player
    testGuild = 1234

    addGuildTable(testGuild)

    player1 = Player(1, 108305168, "Moff", 1234)
    player2 = Player(2, 176488059, "BowiE", 1234)
    player3 = Player(3, 177214200, "Josh", 1234)
    player4 = Player(4, 295355615, "Mumbo", 1234)
    player5 = Player(5, 60623475, "Liver", 1234)
    player6 = Player(6, 121958788, "Ryan", 1234)
    player7 = Player(7, 106614459, "iaa", 1234)
    player8 = Player(8, 141671423, "FooSquash", 1234)
    player9 = Player(9, 108288202, "Fell", 1234)
    player10 = Player(10, 250970093, "Buying Onions", 1234)

    pool = [player1, player2, player3, player4, player5, player6, player7, player8, player9, player10]

    LoIDs = []
    for player in pool:
        player.add()
        LoIDs.append(player.steam_id)

    addMatch(testGuild, 12345, 0, LoIDs)
    addMatch(testGuild, 6783, 0, LoIDs)

    print(getListOfMatchIds(testGuild))
