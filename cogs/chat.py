import discord
from discord.ext import commands
from discord import app_commands


class chat(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name='chat', description="Let the bot Speak")
    async def chat(self, say, *, arg: str):
        await say.response.send_message(arg)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(chat(client))
