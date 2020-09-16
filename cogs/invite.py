import discord
from discord.ext import commands


class Invite(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.invites = dict()

    @commands.Cog.listener()
    async def on_ready(self):
        # Initialize all the invites
        for g in self.bot.guilds:
            await self.update_invites(g)

    def get_invitelog(self, guild):
        return self.bot.conf.get(guild, 'invitelog')

    async def update_invites(self, guild):
        self.invites[guild.id] = await guild.invites()

    def set_invitelog(self, guild, channelid):
        return self.bot.conf.set(guild, 'invitelog', channelid)

    @commands.group(invoke_without_command=True)
    async def invite(self, ctx):
        """Manages invites."""
        pass

    @invite.command()
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        """Gets/Sets the notification channel for invites."""
        if channel is not None:
            self.set_invitelog(ctx.guild.id, channel.id)
            await ctx.send(f"Channel {channel.mention} ist jetzt der Channel für den Invite-Log.")
            return

        channel = self.get_invitelog(ctx.guild.id)

        if channel is None:
            await ctx.send(f"Es ist momentan kein Channel für den Invite-Log gesetzt.")
            return

        await ctx.send(f"Channel <#{channel}> ist der Channel für den Invite-Log.")
        return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.update_invites(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = self.bot.get_channel(int(self.get_invitelog(guild.id)))
        if channel is None:
            return

        old = self.invites[guild.id]
        self.invites[guild.id] = await guild.invites()

        for index, invite in enumerate(old):
            if invite not in self.invites[guild.id]:
                inviter = invite.inviter
                await channel.send(
                    f"**{member}** ({member.id}) wurde von **{inviter}** ({inviter.id}) eingeladen. (Onetime)")
                break
            else:
                if invite.uses != self.invites[guild.id][index].uses:
                    inviter = invite.inviter
                    await channel.send(
                        f"**{member}** ({member.id}) wurde von **{inviter}** ({inviter.id}) eingeladen. "
                        f"(Invite: {invite.code})")
                    break
        else:
            await channel.send("Konnte Invite nicht tracken!")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.update_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.update_invites(invite.guild)


def setup(bot):
    bot.add_cog(Invite(bot))
