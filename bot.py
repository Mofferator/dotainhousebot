import discord
import playerdb
import player

client = discord.Client()

currentJoinMessage = 0

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
        global currentJoinMessage
        currentJoinMessage = sent.id
    
    if message.content.startswith('$addme'):
        reply = addMember(message)
        await message.channel.send(reply)

    if message.content.startswith('$removeme'):
        reply = removeMember(message)
        await message.channel.send(reply)

    if message.content.startswith('$steam'):
        results = playerdb.getPlayer(message.author.id, message.guild.id)
        if results != []:
            reply = results[0][2]
        else:
            reply = "Player not found"
        await message.channel.send(reply)

@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == currentJoinMessage:
        addMember(payload)

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
    return "https://steamcommunity.com/id/" + str(sid)

client.run('OTIzNTQ2Mzg1NDM1OTgzODcy.YcRlmA.ztc9w45Vz8mMD2Z8NVg-HG0TMSY')