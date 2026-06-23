from typing import Any, Coroutine
import discord
from discord import app_commands, ChannelType
from discord.ext import commands, tasks
import asyncio
import humanfriendly
import time as pyTime
import sqlite3
import json, random

database = sqlite3.connect("giveaway.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS giveaways(time INT, prize TEXT, guild_id INT, channel_id INT, message_id INT, participants TEXT, winners INT, finished BOOL)")

class JoinGiveaway(discord.ui.View):
    def __init__(self, guild, time, prize, epochEnd, client):
        super().__init__(timeout=time)
        self.prize = prize
        self.guild = guild
        self.time = epochEnd
        self.client = client

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            await self.message.edit(view=self)
    
    @discord.ui.button(label="Join Giveaway 🎉", style=discord.ButtonStyle.blurple, custom_id="Join")
    async def Join(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.guild, self.prize, self.time)
        data = cursor.execute(f"SELECT * FROM giveaways WHERE guild_id = ? AND prize = ? AND time = ?", (self.guild, self.prize, self.time)).fetchall()
        print(data)
        if data:
            for var in data:
                participants = var[5]
            
            try:
                participants = json.loads(participants)
            except:
                participants = []
            if interaction.user.id in participants:
                await interaction.response.send_message(f"You have already joined this giveaway!", ephemeral=True)
            else:
                participants.append(interaction.user.id)
                cursor.execute("UPDATE giveaways SET participants = ? WHERE guild_id = ? AND prize = ? AND time = ?", (json.dumps(participants), self.guild, self.prize, self.time))
                database.commit()
                await interaction.response.send_message("You joined the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("This giveaway doesn't exist or has already ended", ephemeral=True)



class Giveaway(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.check_giveaways.start()

    def cog_unload(self) ->  None:
        self.check_giveaways.stop()


    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        current_time = pyTime.time()
        data = cursor.execute(f"SELECT * FROM giveaways WHERE time <= {int(current_time)}").fetchall()
        if not data:
            return
        for d in data:
            message_id = d[4]
            epochEnd = d[0]
            prize = d[1]
            channel_id = d[3]
            participants = d[5]
            winners_count = d[6]
            guild_id = d[2]

            try:
                participants = json.loads(participants)
            except:
                participants = []

            channel= self.client.get_guild(guild_id).get_channel(channel_id)
            msg = await channel.fetch_message(message_id)

            if not participants:
                embed = discord.Embed(title="🎉Giveaway!🎉", description=f'{prize}\n Ended at <t:{int(pyTime.time())}:R>\nWinner(s): None \nEntries: 0\nGiveaway ended')
                await channel.send(f"No one participated in the giveaway!")
                await msg.edit(embed=embed)
                cursor.execute(f"DELETE FROM giveaways WHERE guild_id = ? AND message_id = ?", (guild_id, message_id))
                database.commit()
                return 
            
            p_count = len(participants)

            winners = []
            for var in range(winners_count):
                p = random.choice(participants)
                winners.append(p)
                participants.remove(p)

            winner_string = ""
            for w in winners:
                winner_string += f"<@{w}> "
            
            embed = discord.Embed(title="🎉Giveaway!🎉", description=f'{prize}\n Ended at <t:{int(pyTime.time())}:R>\nWinner(s): {winner_string} \nEntries: **{p_count}**\nGiveaway ended')
            await msg.edit(embed=embed, view=None)
            await channel.send(f"{winner_string} won the Giveaway!")
            cursor.execute(f"DELETE FROM giveaways WHERE guild_id = ? AND message_id = ?", (guild_id, message_id))
            database.commit()


    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.wait_until_ready()
        await asyncio.sleep(2)
        print("Database Status: Online")
    
    @app_commands.command(name='giveaway', description="start a giveaway")
    @commands.has_permissions(manage_messages=True)
    async def giveaway(self, interaction: discord.Interaction, prize: str, channel: discord.TextChannel, time: str, winners: int):
        if not channel.permissions_for(interaction.user).send_messages:
            return interaction.response.send_message(f"You don't have permissions to make a giveaway in that channel!")
        time = humanfriendly.parse_timespan(time)
        epochEnd = round(pyTime.time() + time, 5)
        query = "INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (epochEnd, prize, interaction.guild.id, channel.id, "", "", winners, 0))
        database.commit()
        embed = discord.Embed(title="🎉Giveaway!🎉", description=f'{prize}\n Ends at <t:{int(epochEnd)}:R>\nWinner(s): {winners}\n\nClick the "Join Giveaway 🎉" Button to join.')
        await interaction.response.send_message(f"Started giveaway in {channel.mention}", ephemeral=True)
        view = JoinGiveaway(interaction.guild.id, time, prize, epochEnd, self.client)
        msg = await channel.send(embed=embed, view=view)
        view.message = msg
        query1 = ("UPDATE giveaways SET message_id = ? WHERE guild_id = ? AND prize = ? AND time = ?")
        cursor.execute(query1, (msg.id, interaction.guild.id, prize, epochEnd))
        database.commit()


    @app_commands.command(name='giveaway_end', description="end a giveaway")
    @commands.has_permissions(manage_messages=True)
    async def giveaway_end(self, interaction: discord.Interaction, message_id: str):
        message = int(message_id)
        data = cursor.execute(f"SELECT * FROM giveaways WHERE guild_id = ? AND message_id = ?", (interaction.guild.id, message)).fetchall()
        for var in data:
            epochEnd = var[0]
            prize = var[1]
            channel_id= var [3]
            participants = var[5]
            winners_count = var[6]
        channel= self.client.get_guild(interaction.guild.id).get_channel(channel_id)
        msg = await channel.fetch_message(message)
        try:
            participants = json.loads(participants)
        except:
            participants = []

        if not participants:
            embed = discord.Embed(title="🎉Giveaway!🎉", description=f'{prize}\n Ended at <t:{int(pyTime.time())}:R>\nWinner(s): None \nEntries: 0\nGiveaway ended')
            await interaction.response.send_message(f"Giveaway ended.")
            await channel.send(f"No one participated in the giveaway!")
            await msg.edit(embed=embed)
            cursor.execute(f"DELETE FROM giveaways WHERE guild_id = ? AND message_id = ?", (interaction.guild.id, message))
            database.commit()
            return
        
        p_count = len(participants)

        winners = []
        for var in range(winners_count):
            p = random.choice(participants)
            winners.append(p)
            participants.remove(p)

        winner_string = ""
        for w in winners:
            winner_string += f"<@{w}> "
        
        embed = discord.Embed(title="🎉Giveaway!🎉", description=f'{prize}\n Ended at <t:{int(pyTime.time())}:R>\nWinner(s): {winner_string} \nEntries: **{p_count}**\nGiveaway ended')
        await msg.edit(embed=embed, view=None)
        await interaction.response.send_message("Giveaway ended.", ephemeral=True)
        await channel.send(f"{winner_string} won the Giveaway!")
        cursor.execute(f"DELETE FROM giveaways WHERE guild_id = ? AND message_id = ?", (interaction.guild.id, message))
        database.commit()


async def setup(client: commands.bot) -> None:
    await client.add_cog(Giveaway(client))
