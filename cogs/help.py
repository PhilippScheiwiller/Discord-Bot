from typing import Any, Coroutine
import discord
from discord.ext import commands
from discord import app_commands
from discord.interactions import Interaction
from discord.ui import View, Select
import datetime

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", description="Help Menu for Moderation", emoji="🛠️", value="Mod"), 
            discord.SelectOption(label="Configuration", description="Help Menu for Configuration", emoji="⚙️", value="Config"), 
            discord.SelectOption(label="Fun", description="Help Menu for Fun Commands", emoji="🕹️", value="Fun")
            ]
        super().__init__(
            placeholder="Choose a category!",
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        if "Mod" in self.values:
            emb = discord.Embed(title="Moderation Help Menu", description="Some commands may only be used by Moderator", color=0x1338BE, timestamp= datetime.datetime.now())
            emb.add_field(name='/clear', value=f"Delete messages\nAmount not required", inline=False)
            emb.add_field(name='/chat', value=f"let the bot make an announcement", inline=False)
            emb.add_field(name='/ping', value=f"Check bot's ping", inline=False)
            emb.add_field(name='/Giveaway', value=f"start a Giveaway", inline=False)
            emb.add_field(name='/Giveaway_end', value=f"end a Giveaway", inline=False)
            emb.add_field(name='/ticket', value=f"Add a Ticke\nChannel not required", inline=False)
            emb.add_field(name='/close_ticket', value=f"close the Ticket", inline=False)
            emb.add_field(name='/add_to_ticket', value=f"add someone to the Ticket", inline=False)
            emb.add_field(name='/remove_from_ticket', value=f"remove someone from the Ticket", inline=False)
            await interaction.response.send_message(embed=emb, ephemeral=True)
        else:
            if "Config" in self.values:
                emb1 = discord.Embed(title="Configuration Help Menu", description="Only Moderator can use these commands", color=0x1338BE, timestamp= datetime.datetime.now())
                emb1.add_field(name='/welcome_channel', value=f"Set a welcome channel and a message\nChannel and message not required", inline=False)
                emb1.add_field(name='/delete_welcome', value=f"Removes the welcome channel and message", inline=False)
                emb1.add_field(name='/goodbye_channel', value=f"Set a welcome channel and a message\nChannel and message not required", inline=False)
                emb1.add_field(name='/delete_goodbye', value=f"Removes the goodbye channel and message", inline=False)
                emb1.add_field(name='/toggle_leveling', value=f"Enables the leveling system", inline=False)
                emb1.add_field(name='/add_lvl_role', value=f"add a level role", inline=False)
                emb1.add_field(name='/remove_lvl_role', value=f"removes a level role", inline=False)
                await interaction.response.send_message(embed=emb1, ephemeral=True)
            else:
                if "Fun" in self.values:
                    emb2 = discord.Embed(title="Configuration Help Menu", color=0x1338BE, timestamp= datetime.datetime.now())
                    emb2.add_field(name='/emojify', value=f"Emojify your text", inline=False)
                    emb2.add_field(name='/serverinfo', value=f"shows information about the server", inline=False)
                    emb2.add_field(name='/level', value=f"shows your or another members level\nMember not required", inline=False)
                    emb2.add_field(name='/leaderboard', value=f"shows the level leaderboard", inline=False)
                    emb2.add_field(name='/lvlrewards', value=f"shows the level leaderboard", inline=False)
                    await interaction.response.send_message(embed=emb2, ephemeral=True)



class selectmenu(discord.ui.View):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.add_item(HelpSelect())

class help(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name='help', description="Shows a list of commands")
    async def help(self, ctx: discord.Interaction):
        embedvar = discord.Embed(title="Help", description="This is a help command", color=0x1338BE)
        embedvar.add_field(name='Categories', value=f"Choose on of the following categories to find more about the commands", inline=True)
        await ctx.response.send_message(embed=embedvar, view=selectmenu(self.client), ephemeral=True)
        


async def setup(client: commands.Bot) -> None:
    await client.add_cog(help(client))