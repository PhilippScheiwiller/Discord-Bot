import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord import app_commands


database = sqlite3.connect("config.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS ticket(guild_id INT PRIMARY KEY, channel_id INT, user_id INT)")

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

class ticket(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.sync = False
        self.added = False
    
    @commands.Cog.listener()
    async def setup_hook(self) -> None:
        self.client.add_view(ticket_close())
        self.client.add_view(ticket_launcher())



    @app_commands.command(name='ticket', description="Set up a Ticketing System")
    @commands.has_permissions(manage_messages=True)
    async def ticket(self, ctx: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        emb = discord.Embed(title="Ticket", description="If you need Support, create a Ticket using the Button below", color=0x1338BE)
        await channel.send(embed=emb, view= ticket_launcher())
        await ctx.response.send_message("Launched the Ticketing system", ephemeral=True)
    
    @app_commands.command(name='close_ticket', description="close a ticket")
    async def close_ticket(self, interaction: discord.Interaction):
        data = cursor.execute(f"SELECT * FROM ticket WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel.id)).fetchall()
        if not data:
            interaction.response.send_message("You don't have a ticket or your ticket has been already closed", ephemeral=True)
            return
        else:
            for var in data:
                channel_id = var[1]
            if interaction.channel.id != channel_id:
                interaction.response.send_message(f"can't close this Channel, please go to your Ticket and try it again", ephemeral=True)
            else:
                cursor.execute(f"DELETE FROM ticket WHERE guild_id = {interaction.guild.id} AND channel_id = {channel_id}")
                database.commit()
                channel= self.client.get_guild(interaction.guild.id).get_channel(channel_id)
                await channel.delete()

    @app_commands.command(name='add_to_ticket', description="add someone to the ticket")
    @commands.has_permissions(manage_permissions=True)
    async def add_to_ticket(self, interaction: discord.Interaction, user: discord.Member):
        data = cursor.execute(f"SELECT * FROM ticket WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel.id)).fetchall()
        if not data:
            interaction.response.send_message("This isn't a Ticket", ephemeral=True)
            return
        else:
            for var in data:
                channel_id = var[1]
            if interaction.channel.id != channel_id:
                interaction.response.send_message(f"This isn't the Ticket", ephemeral=True)
            else:
                channel= self.client.get_guild(interaction.guild.id).get_channel(channel_id)
                await channel.set_permissions(user, view_channel = True, send_messages =True, read_message_history = True)
                await interaction.response.send_message(f"{user.mention} added to the ticket by {interaction.user.mention}")

    @app_commands.command(name='remove_from_ticket', description="remove someone to the ticket")
    @commands.has_permissions(manage_permissions=True)
    async def remove_from_ticket(self, interaction: discord.Interaction, user: discord.Member):
        data = cursor.execute(f"SELECT * FROM ticket WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel.id)).fetchall()
        if not data:
            interaction.response.send_message("Rhis isn't a Ticket", ephemeral=True)
            return
        else:
            for var in data:
                channel_id = var[1]
            if interaction.channel.id != channel_id:
                interaction.response.send_message(f"This isn't the Ticket", ephemeral=True)
            else:
                if not user.guild_permissions.administrator:
                    channel= self.client.get_guild(interaction.guild.id).get_channel(channel_id)
                    await channel.set_permissions(user, view_channel= False)
                    await interaction.response.send_message(f"{user.mention} added to the ticket by {interaction.user.mention}")



async def setup(client: commands.Bot) -> None:
    await client.add_cog(ticket(client))