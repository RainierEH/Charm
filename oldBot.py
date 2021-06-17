import discord
from discord.ext.commands import Bot
from discord.ext import commands
import json
import asyncio
import sqlite3
from sqlite3 import Error
from datetime import datetime

dPrefix = "!"
bot = commands.Bot(command_prefix=dPrefix)


def sql_connection():
    try:w

        con = sqlite3.connect('warns.db')

        return con

    except Error:

        print(Error)


def sql_table(con):
    global cursorObj

    cursorObj.execute("CREATE TABLE IF NOT EXISTS users(id text PRIMARY KEY, userid text, warning text, date text)")

    con.commit()


con = sql_connection()

cursorObj = con.cursor()

sql_table(con)

initconfig = {
    # DO NOT EDIT THE CONFIG HERE, OR YOU WILL NOT BE ABLE TO EASILY RESTORE SETTINGS
    "token": "BOT_TOKEN",
    # configure which cogs to use
    # core (required), utility, customizable, memes
    "cogs": ["core", "utility", "customizable", "memes"],
}


def tryJSON():
    try:
        f = open("config.json")
        print('[OK] Config "config.json" found, stopping check')
        f.close()
    except IOError:
        print('[ERROR] Default file "config.json" not found, creating new file')
        newConfig()


def newConfig():
    with open("config.json", "w") as f:
        f.write(json.dumps(initconfig, indent=4))


def loadConfig():
    global data
    fn = "config.json"
    with open(fn) as f:
        data = json.load(f)
        f.close()


tryJSON()
loadConfig()


def writeNewID(id):
    with open('warns.txt', 'w') as f:
        f.write(id)


currentWarnID = int(open("warns.txt").read())
print(currentWarnID)


async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
    await bot.change_presence(activity=discord.Streaming(name="Serving" + guild_count + "guilds!", url=""))
    print('Bot Ready')


@bot.command()
async def cheese(ctx):
    await ctx.send(
        "https://images-ext-2.discordapp.net/external/EF5Ow3ziA6sAWrxdcybj7StOxpiBD1DrNzIB07EU1oQ/https/www.campbellrochford.ie/wp-content/uploads/2016/08/Cheese.jpg?width=626&height=610")


@bot.command()
async def uwuify(ctx, *, args):
    await ctx.send(args.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W'))


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)

    embed = discord.Embed(title="Moderation:", colour=discord.Colour(0x3e038c))
    embed.add_field(name=f"Member Banned:", value=member, inline=False)
    embed.add_field(name=f"Reason:", value=reason, inline=False)

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

    embed = discord.Embed(title="Moderation:", colour=discord.Colour(0x3e038c))
    embed.add_field(name=f"Member Kicked:", value=member, inline=False)
    embed.add_field(name=f"Reason:", value=reason, inline=False)

    await ctx.send(embed=embed)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, reason, *, time=0):
    role = discord.utils.get(member.guild.roles, name="Muted")
    await member.add_roles(role)

    embed = discord.Embed(title="Moderation:", colour=discord.Colour(0x3e038c))
    embed.add_field(name=f"Member Muted:", value=member, inline=False)
    embed.add_field(name=f"Reason:", value=reason, inline=False)
    embed.add_field(name=f"Time:", value=str(time) + " Minutes", inline=False)

    await ctx.send(embed=embed)

    await member.send(embed=embed)
    await asyncio.sleep(time * 60)
    await member.remove_roles(role)


@bot.command(pass_context=True)
async def selfid(ctx):
    await ctx.send(str(ctx.message.author.id))


@bot.command(pass_context=True)
async def id(ctx, member: discord.Member):
    await ctx.send(str(member.id))


@bot.command()
async def warn(ctx, member: discord.Member, *, reason):
    global cursorObj
    global currentWarnID
    print(currentWarnID)
    userid = member.id
    date = datetime.today().strftime('%Y-%m-%d')
    insertValues = ("INSERT INTO users VALUES(" + str(currentWarnID) + ", '" + str(userid) + "', '" + str(
        reason) + "', '" + str(date) + "')")
    currentWarnID += 1
    print('Moving up a warn,' + str(currentWarnID))
    writeNewID(str(currentWarnID))
    cursorObj.execute(insertValues)
    # await ctx.send(insertValues)
    con.commit()


@bot.command()
async def log(ctx, member: discord.Member):
    global cursorObj
    insertValues = ("SELECT * FROM users WHERE userid LIKE '%" + str(member.id) + "%'")
    cursorObj.execute(insertValues)
    rows = cursorObj.fetchall()
    embed = discord.Embed(title="Moderation:", colour=discord.Colour(0x3e038c))
    for row in rows:
        embed.add_field(name=f"Warning", value=row, inline=False)
    await ctx.send(embed=embed)


bot.run(data["token"])