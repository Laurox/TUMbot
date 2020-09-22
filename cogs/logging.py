from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_logchannel(self, guild):
        return self.bot.conf.get(guild, 'logchannel')

    def set_logchannel(self, guild, logchannel):
        return self.bot.conf.set(guild, 'logchannel', logchannel)

    async def log_stuff(self, member, message):
        try:
            if member.client:
                logchannelid = self.get_logchannel(member.guild.id)
                if logchannelid is None:
                    return
                logch = self.bot.get_channel(int(logchannelid))
                await logch.send(message)
        except Exception:
            pass
    
    # LogChannel setzen
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx, lchannelid):
        self.set_logchannel(ctx.guild.id, lchannelid)
        await ctx.channel.purge(limit=1)
        await ctx.send("Channel <#" + lchannelid + "> ist jetzt der Channel für den Log.")

    # Memberleave
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_stuff(member, f":outbox_tray: **{member}** ({member.id}) hat den Server verlassen.")

    # Member wird gebannt
    @commands.Cog.listener()
    async def on_member_ban(self, _, member):
        await self.log_stuff(member, f":no_entry_sign: **{member}** ({member.id}) wurde gebannt.")

    # Nachricht löschen
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        try:
            if payload.guild_id is None:
                return

            ch = payload.channel_id
            guild = payload.guild_id
            msg = payload.message_id
            content = payload.cached_message.clean_content
            member = payload.cached_message.author
            channel = payload.cached_message.channel

            logchannelid = self.get_logchannel(member.guild.id)
            if logchannelid is None:
                return

            # Don't log if a bot's message has been deleted (unless it's from the log channel)
            if member.bot and str(logchannelid) != str(channel.id):
                return

            logch = self.bot.get_channel(int(logchannelid))

            # Skip pretty presentation if we are deleting a log message from the log channel
            if member.bot and str(logchannelid) == str(channel.id):
                await logch.send(str(content))
            else:
                await logch.send(
                    f":rcycle: Nachricht ({msg.id}) von **{member}** ({member.id}) in Channel **{channel}** ({ch}) "
                    f"gelöscht mit dem Inhalt:\n{content}")
        except Exception:
            pass


def setup(bot):
    bot.add_cog(Logging(bot))
