import discord
from discord.ext import commands
from discord import app_commands
import asyncio


class moderation(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client    

    @app_commands.command(name='clear', description="Delete messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: discord.Interaction, amount: int = 5):
        await ctx.response.send_message(f"Deleting {amount} messages", ephemeral=True)
        await asyncio.sleep(2)
        await ctx.channel.purge(limit=amount)

    @app_commands.command(name='ban', description="Ban a Player")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: discord.Interaction, user: discord.Member, reason: str = None):
        if reason is None:
            reason = "No reason given"

        if user == ctx.user:
            await ctx.response.send_message("You cannot Ban yourself", ephemeral=True)
            return
        elif user.guild_permissions.administrator:
            await ctx.response.send_message("You cannot Ban an admin", ephemeral=True)
        else:
            await user.ban(reason=reason)
            await ctx.response.send_message(f"Banned {user} for {reason}", ephemeral=True)

    @app_commands.command(name='kick', description="Kick a Player")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: discord.Interaction, user: discord.Member, reason: str = None):
        if reason is None:
            reason = "No reason given"

        if user == ctx.user:
            await ctx.response.send_message("You cannot kick yourself", ephemeral=True)
            return
        elif user.guild_permissions.administrator:
            await ctx.response.send_message("You cannot kick an admin", ephemeral=True)
        else:
            await user.kick(reason=reason)
            await ctx.response.send_message(f"kicked {user} for {reason}", ephemeral=True)
    
    @app_commands.command(name='unban', description="Unban a Player")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: discord.Interaction, user: str):
        try:
            banned_member = await ctx.guild.bans()

            for banned in banned_member:
                member = banned.user

                if member.name == member:
                    await ctx.guild.unban(member[0])
                    await ctx.response.send_message(f"unbanned {member[0].name}", ephemeral=True)
        except:
            await ctx.response.send_message(f"banned member {user} not found", ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(moderation(client))
