import discord
from discord import app_commands
from discord.ext import commands
import random
import requests


class fun(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name='emojify', description="Emojify your Text")
    async def emojify(self, ctx: discord.Interaction, *, text: str):
        emojis = []
        for s in text.lower():
            if s.isdecimal():
                num2emo = {'0': 'zero', '1': 'one', '2': 'two',
                            '3': 'three', '4': 'four', '5': 'five', '6': 'six',
                            '7': 'seven', '8': 'eight', '9': 'nine'}
                emojis.append(f':{num2emo.get(s)}:')
            elif s.isalpha():
                emojis.append(f':regional_indicator_{s}:')
            else:
                emojis.append(s)
        await ctx.response.send_message(''.join(emojis))

    @app_commands.command(name='dice_roll', description="Roll the dice")
    async def dice_roll(self, ctx: discord.Interaction):
        randint = random.randint(1, 6)
        if randint == 1:
            await ctx.response.send_message("1️⃣")
        elif randint == 2:
            await ctx.response.send_message("2️⃣")
        elif randint == 3:
            await ctx.response.send_message("3️⃣")
        elif randint == 4:
            await ctx.response.send_message("4️⃣")
        elif randint == 5:
            await ctx.response.send_message("5️⃣")
        elif randint == 6:
            await ctx.response.send_message("6️⃣")

    @app_commands.command(name='coin_flip', description="Flip a coin")
    async def coin_flip(self, ctx: discord.Interaction):
        randint = random.randint(1, 2)
        if randint == 1:
            await ctx.response.send_message("**Heads**")
        else:
            await ctx.response.send_message("**Tails**")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(fun(client))