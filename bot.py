from sqlite3.dbapi2 import apilevel
import discord
from discord.ext import tasks
import playerdb, apifetch
from player import Player
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv('.env')
TOKEN = os.getenv("TOKEN")

def addMember(m):
    uid = m.author.id
    sid = m.content.removeprefix("$addme ")
    member = m.author.name
    guild_id = m.guild.id
    return playerdb.addPlayer(uid, sid, member, guild_id)

def removeMember(m):
    uid = m.author.id
    gid = m.guild.id
    member = m.author.name
    return playerdb.removePlayer(uid, gid, member)


def steamURL(sid):
    return "https://steamcommunity.com/profiles/" + str(sid)

#converts a discord user object to a player object
def userToPlayer(user_id, guild_id):
    player = playerdb.getPlayer(user_id, guild_id)[0]
    steam_id = player[2]
    member = player[1]
    p = Player(user_id, steam_id, member, guild_id)
    return p

# checks if the author of the given message has the assigned admin role
def checkPerm(message):
    adminRole = playerdb.getSetting(message.guild.id, "adminRole")
    userRoles = message.author.roles
    for role in userRoles:
        if role.name == adminRole:
            return True
    return False

# returns a list of unrecorded match ids for a given guild
def getUnrecorded(guild_id):
    import apifetch
    leagueId = playerdb.getSetting(guild_id, "leagueId")
    recorded = playerdb.getListOfMatchIds(guild_id)
    total = apifetch.getmatchidlist(leagueId)
    unrecorded = []
    for id in total:
        if id not in recorded:
            unrecorded.append(id)
    return unrecorded

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


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.counter = 0

        self.scrapeMatches.start()

    #@client.event
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))

    #@client.event
    async def on_guild_join(self, guild):
        playerdb.addGuildTable(guild.id)

    #@client.event
    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            print(message.channel.id)
            await message.channel.send('Hello!')

        if message.content.startswith('$addplayers'):
            sent = await message.channel.send('React to this message to be added to the inhouse role')
            playerdb.addGuildTable(message.guild.id)
        
        if message.content.startswith('$addme'):
            reply = addMember(message)
            member = message.author
            inhouserRole = playerdb.getSetting(message.guild.id, "role")
            role = discord.utils.get(message.author.guild.roles, name = inhouserRole)
            await message.channel.send(reply)
            await member.add_roles(role)

        if message.content.startswith('$removeme'):
            reply = removeMember(message)
            member = message.author
            inhouserRole = playerdb.getSetting(message.guild.id, "role")
            role = discord.utils.get(message.author.guild.roles, name = inhouserRole)
            await message.channel.send(reply)
            await member.remove_roles(role)

        if message.content.startswith('$steam'):
            results = playerdb.getPlayer(message.author.id, message.guild.id)
            if results != []:
                reply = steamURL(results[0][2])
            else:
                reply = "Player not found"
            await message.channel.send(reply)

        if message.content.startswith("$createinhouse"):
            if checkPerm(message):
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
            
        if message.content.startswith("$setleague"):
            userInput = message.content.removeprefix("$setleague ")
            playerdb.changeSetting(message.guild.id, "leagueId", userInput)
            leagueId = playerdb.getSetting(message.guild.id, "leagueId")
            await message.channel.send("League set to {}".format(leagueId))

        if message.content.startswith("$setrole"):
            userInput = message.content.removeprefix("$setrole ")
            playerdb.changeSetting(message.guild.id, "role", userInput)
            role = playerdb.getSetting(message.guild.id, "role")
            await message.channel.send("Role set to {}".format(role))

        if message.content.startswith("$setadminrole"):
            userInput = message.content.removeprefix("$setadminrole ")
            playerdb.changeSetting(message.guild.id, "adminrole", userInput)
            role = playerdb.getSetting(message.guild.id, "adminrole")
            await message.channel.send("Administrator role set to {}".format(role))

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
            await message.channel.send(embed = formatTeamAssignments(tl[0][0], tl[0][1], message.guild.id))
        
        if message.content.startswith("$setresultschannel"):
            channelId = message.channel.id
            guildId = message.guild.id
            playerdb.changeSetting(guildId, "resultsChannel", channelId)
            

    #@client.event
    async def on_raw_reaction_add(self, payload):
        mid = payload.message_id
        gid = payload.guild_id
        if mid == playerdb.getSetting(gid, "currentJoinId") and payload.member != client.user:
            if payload.emoji.name == '✅':
                print("User {} reacted".format(payload.member.name))

    #923548063539269652
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