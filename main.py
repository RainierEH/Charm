#!/bin/env python3

####################
# DiscCharm/Charm
# Discord bot for utilities and image commands
# https://github.com/RainierEH/Charm
# Made by RainierEH
####################

import json
import sys
import uuid
from datetime import datetime
import discord
from discord.ext import commands
from collections import defaultdict

fn = "config.json"
with open(fn) as f:
    jsonData = json.load(f)
    f.close()

fn = "db.json"
dbData = defaultdict(dict)
with open(fn) as f:
    dbData = json.load(f)
    with open("backupdb.json", "w") as g:
        g.write(json.dumps(dbData))
        g.close()
    f.close()

client = commands.Bot(command_prefix=jsonData["config"]["dUserPrefix"])


@client.event
async def on_ready():
    print("Bot is ready and online!")


@client.event
async def on_guild_join(guild):
    embed = discord.Embed(title="DiscCharm",
                          url="https://github.com/RainierEH/Charm",
                          color=discord.Colour(int(jsonData["config"]["dEmbedColor"], 16)),
                          description=jsonData["config"]["dJoinMessage"])

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
        break


@client.command()
async def uwuify(ctx, *, args):
    embed = discord.Embed(title="Translated Message",
                          color=discord.Colour(int(jsonData["config"]["dEmbedColor"], 16)),
                          description=args.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W'))
    await ctx.send(embed=embed)


@client.command()
async def warn(ctx, member: discord.Member, *, reason):
    global dbData
    uid = str(member.id)

    template = {
            "warns": {
            str(uuid.uuid4()) : [datetime.today().strftime('%Y-%m-%d'), reason, 0]
            },
            "warnCount": 0,
            "mutes": 0,
            "kicks": 0
    }

    addData = [datetime.today().strftime('%Y-%m-%d'), reason, 0]

    try:
        dbData[uid]["warnCount"] += 1
        dbData[uid]["warns"].setdefault(str(uuid.uuid4()), addData)
    except KeyError:
        dbData.setdefault(uid, template)
        dbData[uid]["warnCount"] += 1





    embed = discord.Embed(title="Mod Action:",
                          color=discord.Colour(int(jsonData["config"]["dEmbedColor"], 16)))
    embed.add_field(name=f"Member Warned:",
                    value=member,
                    inline=False)
    embed.add_field(name=f"Reason:",
                    value=reason,
                    inline=False)

    await ctx.send(embed=embed)

    if jsonData["config"]["dAutoWarn"] == 1:
        if dbData[uid]["warnCount"] == jsonData["config"]["dWarnKLimit"]:
            await member.kick(reason=reason)
            uid = str(member.id)
            dbData[uid]["kicks"] += 1

            embed = discord.Embed(title="Mod Action:",
                                color=discord.Colour(int(jsonData["config"]["dEmbedColor"], 16)))
            embed.add_field(name=f"Member Kicked:",
                            value=member,
                            inline=False)
            embed.add_field(name=f"Reason:",
                            value=reason,
                            inline=False)

            await ctx.send(embed=embed)
    else:
        return

@client.command()
@commands.has_permissions(ban_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    global dbData
    uid = str(member.id)
    await member.kick(reason=reason)
    dbData[uid]["kicks"] += 1

    embed = discord.Embed(title="Mod Action:",
                          color=discord.Colour(int(jsonData["config"]["dEmbedColor"], 16)))
    embed.add_field(name=f"Member Kicked:",
                    value=member,
                    inline=False)
    embed.add_field(name=f"Reason:",
                    value=reason,
                    inline=False)

    await ctx.send(embed=embed)

@client.command()
async def shutdown(ctx):
    global dbData
    embed = discord.Embed(title="DiscCharm",
                          url="https://github.com/RainierEH/Charm",
                          color=discord.Colour(int(jsonData["config"]["dEmbedColor"], 16)),
                          description="Bot has been scheduled for a shutdown! Saving data.")

    with open("db.json", "w") as f:
        f.write(json.dumps(dbData, indent=2))
        f.close()

    await ctx.send(embed=embed)
    sys.exit("Shutdown initiated by Discord user")
try:
    client.run(jsonData["config"]["token"])
except KeyboardInterrupt:
    sys.exit('Keyboard Interrupt: Exited Successfully')
