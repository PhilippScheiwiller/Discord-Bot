import discord
import os
import asyncio
import tracemalloc
import sqlite3
import datetime

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

database = sqlite3.connect("config.db")
cursor = database.cursor()


class ticket_launcher(discord.ui.View):
    def __init__(self):
        super().__init__(timeout= None)
    
    @discord.ui.button(label="Create a Ticket", style=discord.ButtonStyle.blurple, custom_id="createticket")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = cursor.execute(f"SELECT * FROM ticket WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id)).fetchall()
        if data:
            await interaction.response.send_message("You already have a Ticket", ephemeral=True)
        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel= False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages =True, read_message_history = True, attach_files= True, embed_links= True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages =True, read_message_history = True, attach_files= True, embed_links= True)
            }
            channel = await interaction.guild.create_text_channel(f"ticket-for-{interaction.user.name}", overwrites=overwrites, reason= f"Ticket for {interaction.user}")
            query = "INSERT INTO ticket VALUES (?, ?, ?)"
            cursor.execute(query, (interaction.guild.id, channel.id, interaction.user.id))
            database.commit()
            await channel.send(f"{interaction.user.mention} created a ticket!", view=ticket_close_confirm())
            await interaction.response.send_message(f"You opened a ticket at {channel.mention}!", ephemeral=True)

class ticket_close(discord.ui.View):
    def __init__(self):
        super().__init__(timeout= None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="closeticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = cursor.execute(f"SELECT * FROM ticket WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel.id)).fetchall()
        try:
            if data:
                cursor.execute(f"DELETE FROM ticket WHERE guild_id = {interaction.guild.id} AND channel_id = {interaction.channel.id}")
                database.commit()
            else:
                return
            await interaction.channel.delete()
        except:
            await interaction.response.send_message(f'Failed to delete channel, make sure i have "manage_channels" permissions!', ephemeral=True)

class ticket_close_confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout= None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="confirmcloseticket")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = discord.Embed(title="Confirmation", description="Are you sure you want to close this ticket?", color=0xFF0800)
        await interaction.response.send_message(embed=emb, view=ticket_close())

class KreativeBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix='.',
            help_command=None,
            intents=discord.Intents.all(),
            application_id=869915623738707968)

    async def setup_hook(self):
        try:
            synced = await client.tree.sync()
            print(f"synced {len(synced)} command(s)")
        except Exception as e:
            print(e)
        self.add_view(ticket_launcher())
        self.add_view(ticket_close_confirm())


client = KreativeBot()

@client.event
async def on_ready():
    tracemalloc.start()
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')
            print(filename[:-3])

    client.loop.create_task(status_task())

    print(f'logged in as {client.user}')
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@client.event
async def on_member_join(member):

    data = cursor.execute(f"SELECT * FROM welcome WHERE guild_id = {member.guild.id}").fetchall()
    data_role = cursor.execute(f"SELECT * FROM autorole WHERE guild_id = {member.guild.id}").fetchall()

    if data:
        for var in data:
            emb = discord.Embed(title="New Member!", color=0xfff00, timestamp=datetime.datetime.now())
            emb.add_field(name=var[2], value= f"{member.mention}", inline=False)
            await client.get_guild(member.guild.id).get_channel(var[1]).send(embed = emb)
    if data_role:
        for var in data:
            role_id = var[1]
            role = member.guild.get_role(role_id)
            try:
                member.add_roles(role)
            except:
                return 


@client.event
async def on_member_remove(member):
    data = cursor.execute(f"SELECT * FROM goodbye WHERE guild_id = {member.guild.id}").fetchall()
    if not data:
        return
    else:
        for var in data:
            emb = discord.Embed(title="Member left!", color=0xfff00, timestamp=datetime.datetime.now())
            emb.add_field(name=var[2], value= f"{member}", inline=False)
            await client.get_guild(member.guild.id).get_channel(var[1]).send(embed = emb)


async def status_task():
    while True:
        await client.change_presence(activity=discord.Game('Kreative bot'))
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name='by kreativetime'))
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for /help"))
        await asyncio.sleep(5)
        

client.run(TOKEN)