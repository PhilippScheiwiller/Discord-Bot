import discord
from discord.ext import commands
from discord import app_commands


class ping(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name='ping', description="Shows Bot's ping")
    async def ping(self, ctx: discord.Interaction):
        await ctx.response.send_message(f'`{self.client.latency} ms`')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ping(client))
