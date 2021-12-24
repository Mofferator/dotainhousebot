import discord
import playerdb
import player
import os
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv("TOKEN")

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_guild_join(guild):
    playerdb.addGuildTable(guild.id)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
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
            await startmsg.add_reaction('✅')
        
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
        for user in users:
            print(user)
        if len(users) < 10:
            await message.channel.send("Not enough players for an inhouse, please add {} more".format(10 - len(users)))
        if len(users) > 10:
            await message.channel.send("Too many players for an inhouse, please remove {} players".format(len(users) - 10))
        


@client.event
async def on_raw_reaction_add(payload):
    mid = payload.message_id
    gid = payload.guild_id
    if mid == playerdb.getSetting(gid, "currentJoinId") and payload.member != client.user:
        if payload.emoji.name == '✅':
            print("User {} reacted".format(payload.member.name))
        else:
            print(payload.emoji.name)
            print(payload.event_type)
            


def addMember(m):
    uid = m.author.id
    sid = m.content.removeprefix("$addme ")
    member = m.author.name
    guild_id = m.guild.id
    p = player.Player(uid, sid, member, guild_id)
    return p.add()

def removeMember(m):
    uid = m.author.id
    gid = m.guild.id
    member = m.author.name
    return playerdb.removePlayer(uid, gid, member)

def steamURL(sid):
    return "https://steamcommunity.com/profiles/" + str(sid)


client.run(TOKEN)