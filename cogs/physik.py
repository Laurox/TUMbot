from discord.ext import commands
import re
import discord
import asyncio
import os

class Physik(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.guild.id == 640285216245809183:
            return

        await member.send(f'Hey {member.mention}, bitte schreibe einem der Admins eine private Nachricht, damit sie hinter deinen Discord-Tag deinen Vornamen setzen können. Um mehr Informationen zu erhalten, schaue in den Textkanal <#702154018490941480>')

def setup(bot):
    bot.add_cog(Physik(bot))
