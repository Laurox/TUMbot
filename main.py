#!/usr/bin/env python3

from pathlib import Path
import os
import re
from subprocess import call

from discord.ext import commands

from bot import Bot
from dbmgr import DbMgr

try:
    dbpath = os.environ['TUMBOT_DBPATH']
except KeyError:
    dbpath = "db"

db = DbMgr(dbpath)

# Finde den Prefix eines Servers
def get_prefix(bot, message):
    if message.guild is None:
        return '!'

    return bot.dbconf_get(message.guild.id, 'prefix', '!')


def find_fqcn(name):
    if os.path.isfile(f"cogs/{name}.py"):
        return f"cogs.{name}"

    if os.path.isfile(f"cogs/legacy/{name}.py"):
        return f"cogs.legacy.{name}"

    return None


bot = Bot(db, command_prefix=get_prefix)


# Bot herunterfahren
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.message.add_reaction('\U00002705')
    await bot.logout()


# Bot updaten
@bot.command()
@commands.is_owner()
async def update(ctx):
    if call(["git", "fetch", "origin", "master"]) == 0 and call(["git", "checkout", "FETCH_HEAD"]) == 0:
        await ctx.message.add_reaction('\U00002705')
    else:
        await ctx.message.add_reaction('\U0001F525')


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Meine Latenz ist aktuell {round(bot.latency * 1000)}ms.')


# Modul laden
@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    e = extension.lower()
    name = find_fqcn(e)

    if name is None:
        await ctx.send(f"Cog `{e}` could not be found.")
        return

    bot.load_extension(name)
    await ctx.message.add_reaction('\U00002705')


# Modul deaktivieren
@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    e = extension.lower()
    name = find_fqcn(e)

    if name is None:
        await ctx.send(f"Cog `{e}` could not be found.")
        return

    bot.unload_extension(name)
    await ctx.message.add_reaction('\U00002705')


# Modul neuladen
@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    e = extension.lower()
    name = find_fqcn(e)

    if name is None:
        await ctx.send(f"Cog `{e}` could not be found.")
        return

    bot.reload_extension(name)
    await ctx.message.add_reaction('\U00002705')


# Beim start alle module laden
for path in Path('cogs').rglob('*.py'):
    name = find_fqcn(path.stem)

    if name is None:
        print(f"Skipped loading Cog `{path.stem}`.")
        continue

    try:
        bot.load_extension(name)
    except Exception as e:
        print(f"Exception while loading `{name}`:")
        print(f"{type(e).__name__}: {e}")

bot.run(os.environ['TUMBOT_TOKEN'])
