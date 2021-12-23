import sqlite3

conn = sqlite3.connect('players.db')

c = conn.cursor()

def addGuildTable(guild_id):
    gid = "guild" + str(guild_id)
    c.execute("CREATE TABLE IF NOT EXISTS {} (user_id integer, member text, steam_id integer)".format(gid))
    conn.commit()

def addPlayer(user_id, steam_id, member, guild_id):
    gid = "guild" + str(guild_id)
    c.execute("SELECT * FROM {} WHERE user_id = ?".format(gid), (user_id,))
    if c.fetchall() == []:
        c.execute("INSERT INTO {} VALUES (?, ?, ?)".format(gid), (user_id, member, steam_id))
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