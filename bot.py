import discord
from discord.ext import tasks
import playerdb, apifetch
from player import Player
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv('.env')
TOKEN = os.getenv("TOKEN")

# Adds the given discord member object to the database
def addMember(m):
    uid = m.author.id
    sid = m.content.removeprefix("$addme ")
    member = m.author.name
    guild_id = m.guild.id
    return playerdb.addPlayer(uid, sid, member, guild_id)

# removes the given discord member object from the data base
def removeMember(m):
    uid = m.author.id
    gid = m.guild.id
    member = m.author.name
    return playerdb.removePlayer(uid, gid, member)

# NOT WORKING, USES STEAM32 INSTEAD OF 64, MAYBE CHANGE TO DOTABUFF URL INSTEAD
def steamURL(sid):
    return "https://steamcommunity.com/profiles/" + str(sid)

#converts a discord user object to a player object as per player.py
def userToPlayer(user_id, guild_id):
    player = playerdb.getPlayer(user_id, guild_id)[0]
    steam_id = player[2]
    member = player[1]
    p = Player(user_id, steam_id, member, guild_id)
    return p

# checks if the author of the given message has the assigned admin role
# admin role can be found in settings<guild_id> table
def checkPerm(member, guild_id):
    adminRole = playerdb.getSetting(guild_id, "adminRole")
    userRoles = member.roles
    for role in userRoles:
        if role.name == adminRole:
            return True
    return False

# returns a list of unrecorded match ids for a given guild
# An "unrecorded" ID is one which is not currently in the matches<guild_id> table in the database
# RETURN: [INT MATCHID]
def getUnrecorded(guild_id):
    import apifetch
    leagueId = playerdb.getSetting(guild_id, "leagueId")
    recorded = playerdb.getListOfMatchIds(guild_id) # get list of recorded matches from the database
    total = apifetch.getmatchidlist(leagueId) # Get list of total matches form STRATZ api 
    unrecorded = []
    for id in total:
        if id not in recorded:
            unrecorded.append(id)
    return unrecorded

# Takes the match info and returns an html embed to be displayed by the bot

# MATCH INFO: (INT MATCHID, INT WINNER, [INT STEAMID], [STRING NAME])
# GUILD ID: INT

# RETURN: EMBED OBJECT
def formatMatch(matchInfo, guild_id):
    matchId = matchInfo[0]
    
    if matchInfo[1] == 0:
        winner = "Radiant"
    else:
        winner = "Dire"

    leagueId = playerdb.getSetting(guild_id, "leagueId")

    icon = "https://riki.dotabuff.com/leagues/" + str(leagueId) + "/icon.png"

    l = matchInfo[3]


    embed=discord.Embed(title="Match {}".format(matchId), url="https://dotabuff.com/matches/" + str(matchId), description="Winner: {}".format(winner), color=0xff0000)
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Radiant", value="{}\n{}\n{}\n{}\n{}\n".format(l[0],l[1],l[2],l[3],l[4]), inline=True)
    embed.add_field(name="Dire", value="{}\n{}\n{}\n{}\n{}\n".format(l[5],l[6],l[7],l[8],l[9]), inline=True)
    return embed

# Takes two lists of player (as per player.py) objects and a guild ID and formats it into a discord embed object to be displayed by the bot
# TEAM1: [PLAYER PLAYER]
# TEAM2: [PLAYER PLAYER]
# GUILD_ID: INT GUILD_ID

# RETURN: DISCORD EMBED OBJECT
def formatTeamAssignments(team1, team2, guild_id):
    numPlayers = len(team1)

    string1 = ""
    string2 = ""

    leagueId = playerdb.getSetting(guild_id, "leagueId")

    icon = "https://riki.dotabuff.com/leagues/" + str(leagueId) + "/icon.png"

    for i in range(numPlayers):
        string1 = string1 + "{}\n".format(team1[0].member)
        string2 = string2 + "{}\n".format(team2[0].member)

    embed=discord.Embed(title="Team Assignments", color=0xff0000)
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Team 1", value=string1, inline=True)
    embed.add_field(name="Team 2", value=string2, inline=True)

    return embed

# Main class, api is managed from here
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.counter = 0

        self.scrapeMatches.start()

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))

    async def on_guild_join(self, guild):
        playerdb.addGuildTable(guild.id)

    async def on_message(self, message):

        # ignore messages from the bot
        if message.author == client.user:
            return

        # Hello test message
        # INPUT: "$hello"
        # OUTCOME: Bot responds with "Hello!"
        if message.content.startswith('$hello'):
            print(message.channel.id)
            await message.channel.send('Hello!')

        # Initialise the server in the bots database
        # INPUT: "$addplayers"
        # OUTCOME: create database tables for the server
        if message.content.startswith('$addplayers'):
            sent = await message.channel.send('React to this message to be added to the inhouse role')
            playerdb.addGuildTable(message.guild.id)
        
        # Add given player to the database
        # INPUT: "$addme STEAM32_ACCOUNT_ID"
        # OUTCOME: The message author is linked to the given steam id in the database, user is also given the assigned inhouse role
        if message.content.startswith('$addme'):
            reply = addMember(message)
            member = message.author
            inhouserRole = playerdb.getSetting(message.guild.id, "role")
            role = discord.utils.get(message.author.guild.roles, name = inhouserRole)
            await message.channel.send(reply)
            await member.add_roles(role)

        # Removes given player from the database
        # INPUT: "$removeme"
        # OUTCOME: Removes the message author from the database, also removes the assigned role
        if message.content.startswith('$removeme'):
            reply = removeMember(message)
            member = message.author
            inhouserRole = playerdb.getSetting(message.guild.id, "role")
            role = discord.utils.get(message.author.guild.roles, name = inhouserRole)
            await message.channel.send(reply)
            await member.remove_roles(role)

        # CURRENTLY DOESN'T WORK
        # INPUT: "$steam"
        # OUTCOME: Displays the users steam URL
        if message.content.startswith('$steam'):
            results = playerdb.getPlayer(message.author.id, message.guild.id)
            if results != []:
                reply = steamURL(results[0][2])
            else:
                reply = "Player not found"
            await message.channel.send(reply)

        # Creates an inhouse session in the server. Can only be issued by users with the assigned admin role
        # INPUT: "$createinhouse"
        # OUTCOME: Sends a message the players can react to, to be added to the inhouse. The inhouse can then be started with $startinhouse
        if message.content.startswith("$createinhouse"):
            if checkPerm(message.author, message.guild.id):
                startmsg = 0
                leagueId = playerdb.getSetting(message.guild.id, "leagueId")
                if leagueId == 0:
                    await message.channel.send("No league currently configured for this server...")
                elif leagueId == -1:
                    embed=discord.Embed(title="Inhouse Starting...", description="React to this message with a checkmark to join")
                    startmsg = await message.channel.send(embed=embed)
                else:
                    embed=discord.Embed(title="Inhouse Starting for league: {}...".format(leagueId), description="React to this message with a checkmark to join")
                    startmsg = await message.channel.send(embed=embed)
                if startmsg != 0:
                    playerdb.changeSetting(message.guild.id, "currentJoinId", startmsg.id)
                    playerdb.changeSetting(message.guild.id, "currentJoinTime", startmsg.created_at.timestamp())
                    await startmsg.add_reaction('✅')
            else:
                await message.channel.send("You don't have permission to do that")
            
        # Sets the league to the given value for the server
        # INPUT: "$setleague LEAGUE_ID"
        # OUTCOME: changes the league setting in the SETTING<guild_id> table to the given value
        if message.content.startswith("$setleague"):
            userInput = message.content.removeprefix("$setleague ")
            playerdb.changeSetting(message.guild.id, "leagueId", userInput)
            leagueId = playerdb.getSetting(message.guild.id, "leagueId")
            await message.channel.send("League set to {}".format(leagueId))

        # Sets the inhouse role to the given value
        # INPUT: "$setrole ROLE_NAME"
        # OUTCOME: Changes the role setting in the SETTING<guild_id> table to the given value
        if message.content.startswith("$setrole"):
            userInput = message.content.removeprefix("$setrole ")
            playerdb.changeSetting(message.guild.id, "role", userInput)
            role = playerdb.getSetting(message.guild.id, "role")
            await message.channel.send("Role set to {}".format(role))

        # Sets the admin role to the given value
        # INPUT: "$setadminrole ROLE_NAME"
        # OUTCOME: Changes the admin role setting in the SETTING<guild_id> table to the given value
        if message.content.startswith("$setadminrole"):
            userInput = message.content.removeprefix("$setadminrole ")
            playerdb.changeSetting(message.guild.id, "adminrole", userInput)
            role = playerdb.getSetting(message.guild.id, "adminrole")
            await message.channel.send("Administrator role set to {}".format(role))

        # Starts the inhouse by locking in players and generating balanced teams
        # INPUT: "$startinhouse"
        # OUTCOME: Collects the users who reacted and generates balanced teams. Creates a new message displaying the teams with a button to move people
        #          into voice channels
        if message.content.startswith("$startinhouse"):

            channel = message.channel
            joinMessageId = playerdb.getSetting(message.guild.id, "currentJoinId")
            joinMessage = await channel.fetch_message(joinMessageId)
            listOfReactions = joinMessage.reactions # get all reactions from inhouse creation message
            checkReaction = 0
            for reaction in listOfReactions:
                if reaction.emoji == '✅': # find only the checkmark reactions
                    checkReaction = reaction
            users = await checkReaction.users().flatten()
            users.remove(client.user) # remove bot from list of reactors
            #if len(users) < 10:
                #await message.channel.send("Not enough players for an inhouse, please add {} more".format(10 - len(users)))
            #elif len(users) > 10:
                #await message.channel.send("Too many players for an inhouse, please remove {} players".format(len(users) - 10))
            #else:
            import teamGeneration
            listOfPlayers = []
            for user in users:
                listOfPlayers.append(userToPlayer(user.id, message.guild.id))
            tl = teamGeneration.genteamlist(listOfPlayers)
            reply = teamGeneration.formatTeams(tl[0])
            sentMessage = await message.channel.send(embed = formatTeamAssignments(tl[0][0], tl[0][1], message.guild.id))
            playerdb.changeSetting(message.guild.id, "currentStartId", sentMessage.id)
            await sentMessage.add_reaction('✅')
        
        # Sets the results channel to the channel the message was posted in
        # INPUT: "$setresultschannel"
        # OUTCOME: Sets the results channel to the channel the message was posted in
        if message.content.startswith("$setresultschannel"):
            channelId = message.channel.id
            guildId = message.guild.id
            playerdb.changeSetting(guildId, "resultsChannel", channelId)

        # Sets the voice channel for team1 to the channel the user is currently connected to
        # INPUT: "$setteam1channel"
        # OUTCOME: Sets the team1channel setting to the channel ID that the command issuer is connected to 
        if message.content.startswith("$setteam1channel"):
            from playerdb import changeSetting
            if checkPerm(message.author, message.guild.id):
                channelId = message.author.voice.channel.id
                changeSetting(message.guild.id, "team1Channel", channelId)
            else:
                await message.channel.send("You don't have permission to do that")

        # Sets the voice channel for team2 to the channel the user is currently connected to
        # INPUT: "$setteam2channel"
        # OUTCOME: Sets the team2channel setting to the channel ID that the command issuer is connected to
        if message.content.startswith("$setteam2channel"):
            from playerdb import changeSetting
            if checkPerm(message.author, message.guild.id):
                channelId = message.author.voice.channel.id
                changeSetting(message.guild.id, "team2Channel", channelId)
            else:
                await message.channel.send("You don't have permission to do that")

    #@client.event
    async def on_raw_reaction_add(self, payload):
        mid = payload.message_id
        gid = payload.guild_id
        guild = client.get_guild(gid)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        print(guild)
        if mid == playerdb.getSetting(gid, "currentStartId") and payload.member != client.user:
            if payload.emoji.name == '✅':
                if checkPerm(payload.member, gid):
                    import teamGeneration
                    joinMessageId = playerdb.getSetting(gid, "currentJoinId")
                    joinMessage = await channel.fetch_message(joinMessageId)
                    listOfReactions = joinMessage.reactions # get all reactions from inhouse creation message
                    checkReaction = 0
                    for reaction in listOfReactions:
                        if reaction.emoji == '✅': # find only the checkmark reactions
                            checkReaction = reaction
                    users = await checkReaction.users().flatten()
                    users.remove(client.user)
                    listOfPlayers = []
                    for user in users:
                        listOfPlayers.append(userToPlayer(user.id, gid))
                    tl = teamGeneration.genteamlist(listOfPlayers)
                    team1ChannelID = playerdb.getSetting(gid, "team1Channel")
                    team2ChannelID = playerdb.getSetting(gid, "team2Channel")
                    team1Channel = guild.get_channel(team1ChannelID)
                    team2Channel = guild.get_channel(team2ChannelID)
                    members = []
                    for user in users:
                        member = await guild.fetch_member(user.id)
                        members.append(member)
                    for player in tl[0][0]:
                        for user in members:
                            if player.user_id == user.id:
                                await user.move_to(team1Channel)
                    for player in tl[0][1]:
                        for user in members:
                            if player.user_id == user.id:
                                await user.move_to(team2Channel)



    @tasks.loop(seconds=60) # task runs every 60 seconds
    async def scrapeMatches(self):
        for g in self.guilds:
            guild_id = g.id
            joinMessageTime = playerdb.getSetting(guild_id, "currentJoinTime")
            now = datetime.now().timestamp()
            if now - int(joinMessageTime) < 86400:
                unrecorded = getUnrecorded(guild_id)
                for matchId in unrecorded:
                    matchInfo = apifetch.getMatchInfo(matchId)
                    if matchInfo != 0:
                        playerdb.addMatch(guild_id, matchInfo[0], matchInfo[1], matchInfo[2], matchInfo[3])
                        channel = self.get_channel(playerdb.getSetting(guild_id, "resultsChannel"))
                        await channel.send(embed=formatMatch(matchInfo, guild_id))


    @scrapeMatches.before_loop
    async def before_my_task(self):
        await self.wait_until_ready() # wait until the bot logs in


client = MyClient()
client.run(TOKEN)