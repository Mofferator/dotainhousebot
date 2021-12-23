class Player:
    def __init__(self, user_id, steam_id, member, guild_id):
        self.user_id = user_id
        self.steam_id = steam_id
        self.member = member
        self.guild_id = guild_id

    def add(self):
        import playerdb
        print("Adding player: {}".format(self.member))
        return playerdb.addPlayer(self.user_id, self.steam_id, self.member, self.guild_id)

    def remove(self):
        import playerdb
        print("Removing player: {}".format(self.member))
        return playerdb.removePlayer(self.user_id, self.steam_id, self.member, self.guild_id)

    