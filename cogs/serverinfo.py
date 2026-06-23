import discord
from discord.ext import commands
from discord import app_commands


class serverinfo(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name='serverinfo', description="Show Server stats")
    async def serverinfo(self, ctx: discord.Interaction):
        role_count = len(ctx.guild.roles)

        serverinfoembed = discord.Embed(color=0x7289da)
        serverinfoembed.add_field(name='Name', value=f"{ctx.guild.name}", inline=False)
        serverinfoembed.add_field(name='Member Count', value=str(ctx.guild.member_count), inline=False)
        serverinfoembed.add_field(name='Verification Level', value=str(ctx.guild.verification_level), inline=False)
        serverinfoembed.add_field(name='Highest Role', value=ctx.guild.roles[-1], inline=False)
        serverinfoembed.add_field(name='Number of Roles', value=str(role_count), inline=False)
        serverinfoembed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.response.send_message(embed=serverinfoembed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(serverinfo(client))
