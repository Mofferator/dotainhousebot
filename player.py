import apifetch
import playerdb

class Player:
    def __init__(self, user_id, steam_id, member, guild_id):
        self.user_id = user_id
        self.steam_id = steam_id
        self.member = member
        self.guild_id = guild_id
        if (playerdb.getMMROveride(guild_id, user_id) == 0):
            self.mmr = apifetch.getplayermmr(steam_id)
        else:
            self.mmr = playerdb.getMMROveride(guild_id, user_id)

    def add(self):
        import playerdb
        print("Adding player: {}".format(self.member))
        return playerdb.addPlayer(self.user_id, self.steam_id, self.member, self.guild_id)

    def remove(self):
        import playerdb
        print("Removing player: {}".format(self.member))
        return playerdb.removePlayer(self.user_id, self.steam_id, self.member, self.guild_id)

if __name__ == "__main__":
    player1 = Player(12, 108305168, "Moff", 1234)
    print(player1.mmr)