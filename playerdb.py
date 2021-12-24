import sqlite3

conn = sqlite3.connect('players.db')

c = conn.cursor()

def addGuildTable(guild_id):
    gid = "guild" + str(guild_id)
    settingsId = "settings" + str(guild_id)
    c.execute("CREATE TABLE IF NOT EXISTS {} (user_id integer, member text, steam_id integer, mmr_overide integer)".format(gid))
    c.execute("CREATE TABLE IF NOT EXISTS {} (leagueId integer, currentJoinId integer, role text)".format(settingsId))
    c.execute("INSERT INTO {} VALUES (?, ?, ?)".format(settingsId), (0, 0, ""))
    conn.commit()

def addPlayer(user_id, steam_id, member, guild_id):
    gid = "guild" + str(guild_id)
    c.execute("SELECT * FROM {} WHERE user_id = ?".format(gid), (user_id,))
    if c.fetchall() == []:
        c.execute("INSERT INTO {} VALUES (?, ?, ?, 0)".format(gid), (user_id, member, steam_id))
        conn.commit()
        return "Player {} added to database".format(member)
    else:
        print(c.fetchall())
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