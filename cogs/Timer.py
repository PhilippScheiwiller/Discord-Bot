from typing import Any, Coroutine
import discord
from discord import app_commands, ChannelType
from discord.ext import commands, tasks
import humanfriendly
import time as pyTime
import sqlite3

database = sqlite3.connect("timer.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS timer(time INT, guild_id INT, channel_id INT, message TEXT, user_id INT)")

class Timer(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.check_Timer.start()

    def cog_unload(self) ->  None:
        self.check_Timer.stop()


    @tasks.loop(seconds=5)
    async def check_Timer(self):
        current_time = pyTime.time()
        data = cursor.execute(f"SELECT * FROM timer WHERE time <= {int(current_time)}").fetchall()
        if not data:
            return
        for d in data:
            epochEnd = d[0]
            guild_id = d[1]
            channel_id = d[2]
            notification = d[3]
            user_id = d[4]

            channel= self.client.get_guild(guild_id).get_channel(channel_id)
            
            embed = discord.Embed(title="Timer!", description=f'Timer ended at <t:{int(pyTime.time())}:R>\nNotification: {notification}')
            await channel.send(f"<@{user_id}> your Timer ended.", embed=embed)
            cursor.execute(f"DELETE FROM timer WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            database.commit()

    
    @app_commands.command(name='timer', description="Set a Timer")
    async def timer(self, interaction: discord.Interaction, channel: discord.TextChannel, time: str, notification: str = None):
        data = cursor.execute(f"SELECT * FROM timer WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id)).fetchall()
        if data:
            await interaction.response.send_message("You already have a Timer", ephemeral=True)
            return
        if notification == None:
            notification = "No Notification"
        if not channel.permissions_for(interaction.user).send_messages:
            return interaction.response.send_message(f"You don't have permissions to set a timer in that channel!")
        time = humanfriendly.parse_timespan(time)
        epochEnd = round(pyTime.time() + time, 5)
        query = "INSERT INTO timer VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (epochEnd, interaction.guild.id, channel.id, notification, interaction.user.id))
        database.commit()
        await interaction.response.send_message(f"Set up a Timer that ends at <t:{int(epochEnd)}:R>", ephemeral=True)


    @app_commands.command(name='delete_timer', description="delete a timer")
    async def delete_timer(self, interaction: discord.Interaction):
        data = cursor.execute(f"SELECT * FROM timer WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id)).fetchall()
        if data:
            await interaction.response.send_message("Deleting your Timer")
            cursor.execute(f"DELETE FROM timer WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
            database.commit()
        else:
            await interaction.response.send_message("You don't have a Timer")


async def setup(client: commands.bot) -> None:
    await client.add_cog(Timer(client))