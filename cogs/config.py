import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

database = sqlite3.connect("config.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS welcome(guild_id INT PRIMARY KEY, channel_id INT, message_content STRING)")
database.execute("CREATE TABLE IF NOT EXISTS goodbye(guild_id INT PRIMARY KEY, channel_id INT, message_content STRING)")
database.execute("CREATE TABLE IF NOT EXISTS levelSettings(guild_id INT PRIMARY KEY, enable BOOL)")
database.execute("CREATE TABLE IF NOT EXISTS levelrewards(guild_id INT, role INT, level_req INT)")
database.execute("CREATE TABLE IF NOT EXISTS autorole(guild_id INT, role INT)")

class config(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(name='welcome_channel', description="Set the Welcome channel and message")
    @commands.has_permissions(manage_messages=True)
    async def welcome_channel(self, ctx: discord.Interaction, new_channel: discord.TextChannel = None, message: str = None):
        data = cursor.execute(f"SELECT * FROM welcome WHERE guild_id = {ctx.guild.id}").fetchall()
        channel = 0
        if not data:
            if message is None:
                message = "Welcome to the server"
            if new_channel is None:
                channel = ctx.channel.id
            else:
                channel = new_channel.id
            query = "INSERT INTO welcome VALUES (?, ?, ?)"
            cursor.execute(query, (ctx.guild.id, channel, message))
            database.commit()

            await ctx.response.send_message(f"<#{channel}> has been configured as the welcome channel")
        else:
            for var in data:
                if message is None:
                    message = var[2]
                if new_channel is None:
                    channel = var[1]
                else:
                    if new_channel is not None:
                        channel = new_channel.id
            query = "UPDATE welcome SET channel_id = ?, message_content = ? WHERE guild_id = ?"
            cursor.execute(query, (channel, message, ctx.guild.id))
            database.commit()

            await ctx.response.send_message(f"The welcome channel has been")


    @app_commands.command(name='goodbye_channel', description="Set the Goodbye channel and message")
    @commands.has_permissions(manage_messages=True)
    async def goodbye_channel(self, ctx: discord.Interaction, new_channel: discord.TextChannel = None, message: str = None):
        data = cursor.execute(f"SELECT * FROM goodbye WHERE guild_id = {ctx.guild.id}").fetchall()
        channel = 0
        if not data:
            if message is None:
                message = "Goodbye"
            if new_channel is None:
                channel = ctx.channel.id
            else:
                channel = new_channel.id
            query = "INSERT INTO goodbye VALUES (?, ?, ?)"
            cursor.execute(query, (ctx.guild.id, channel, message))
            database.commit()

            await ctx.response.send_message(f"<#{channel}> has been configured as the goodbye channel")
        else:
            for var in data:
                if message is None:
                    message = var[2]
                if new_channel is None:
                    channel = var[1]
                else:
                    if new_channel is not None:
                        channel = new_channel.id
            query = "UPDATE goodbye SET channel_id = ?, message_content = ? WHERE guild_id = ?"
            cursor.execute(query, (channel, message, ctx.guild.id))
            database.commit()

            await ctx.response.send_message(f"The goodbye channel has been Updated")
    
    @app_commands.command(name='delete_goodbye', description="Delete the Goodbye channel and message")
    @commands.has_permissions(manage_messages=True)
    async def delete_goodbye(self, ctx: discord.Interaction):
        data = cursor.execute(f"SELECT * FROM goodbye WHERE guild_id = {ctx.guild.id}").fetchall()
        if not data:
            await ctx.response.send_message("No goodbye data found")
            return
        cursor.execute(f"DELETE FROM goodbye WHERE guild_id = {ctx.guild.id}")
        await ctx.response.send_message("Sucessfully deleted goodbye data")

    @app_commands.command(name='delete_welcome', description="Delete the Goodbye channel and message")
    @commands.has_permissions(manage_messages=True)
    async def delete_welcome(self, ctx: discord.Interaction):
        data = cursor.execute(f"SELECT * FROM welcome WHERE guild_id = {ctx.guild.id}").fetchall()
        if not data:
            await ctx.response.send_message("No welcome data found")
            return
        cursor.execute(f"DELETE FROM welcome WHERE guild_id = {ctx.guild.id}")
        await ctx.response.send_message("Sucessfully deleted welcome data")

    @app_commands.command(name='toggle_leveling', description="enable/disable the leveling system")
    @commands.has_permissions(manage_guild=True)
    async def toggle_leveling(self, ctx: discord.Interaction):
        data = cursor.execute(f"SELECT * FROM levelSettings WHERE guild_id = {ctx.guild.id}").fetchall()
        if not data:
            query = "INSERT INTO levelSettings VALUES (?, ?)"
            cursor.execute(query, (ctx.guild.id, 1))
            database.commit()
            await ctx.response.send_message(f"enabled Leveling system for this Server")
        else:
            for var in data:
                enable_bool = var[1]
            if enable_bool == 1:
                query = "UPDATE levelSettings SET enable = ? WHERE guild_id = ?"
                cursor.execute(query, (0, ctx.guild.id))
                database.commit()
                await ctx.response.send_message(f"disabled Leveling system for this Server")
            elif enable_bool == 0:
                query = "UPDATE levelSettings SET enable = ? WHERE guild_id = ?"
                cursor.execute(query, (1, ctx.guild.id))
                database.commit()
                await ctx.response.send_message(f"enabled Leveling system for this Server")

    @app_commands.command(name='add_lvl_role', description="add a level role")
    @commands.has_permissions(manage_messages=True)
    async def add_lvl_role(self, ctx: discord.Interaction, level_req: int, role: discord.Role):
        check = cursor.execute(f"SELECT * FROM levelSettings WHERE guild_id = {ctx.guild.id}").fetchall()
        if not check:
            await ctx.response.send_message("This guild doesn't allow leveling", ephemeral=True)
            return
        else:
            for var in check:
                enable_bool = var[1]
            if enable_bool == 0:
                await ctx.response.send_message("This guild doesn't allow leveling", ephemeral=True)
                return
        data_role = cursor.execute(f"SELECT * FROM levelrewards WHERE guild_id = {ctx.guild.id} AND role = {role.id}").fetchall()
        data_level = cursor.execute(f"SELECT * FROM levelrewards WHERE guild_id = {ctx.guild.id} AND level_req = {level_req}").fetchall()
        if data_level or data_role:
            return await ctx.response.send_message("a role/level-requirement setting already exists")
        query = "INSERT INTO levelrewards VALUES (?, ?, ?)"
        cursor.execute(query, (ctx.guild.id, role.id, level_req))
        database.commit()
        await ctx.response.send_message("updated the level Role")

    @app_commands.command(name='remove_lvl_role', description="removes a level role")
    @commands.has_permissions(manage_messages=True)
    async def remove_lvl_role(self, ctx: discord.Interaction, level_req: int):
        check = cursor.execute(f"SELECT * FROM levelSettings WHERE guild_id = {ctx.guild.id}").fetchall()
        if not check:
            await ctx.response.send_message("This guild doesn't allow leveling", ephemeral=True)
            return
        else:
            for var in check:
                enable_bool = var[1]
            if enable_bool == 0:
                await ctx.response.send_message("This guild doesn't allow leveling", ephemeral=True)
                return
        data_level = cursor.execute(f"SELECT * FROM levelrewards WHERE guild_id = {ctx.guild.id} AND level_req = {level_req}").fetchall()
        if not data_level:
            return await ctx.response.send_message(" role setting doesn't exists")
        cursor.execute(f"DELETE FROM levelrewards WHERE guild_id = {ctx.guild.id} AND level_req = {level_req}")
        database.commit()
        await ctx.response.send_message("removed the level Role")

    @app_commands.command(name='add_autorole', description="add a autorole")
    @commands.has_permissions(manage_messages=True)
    async def add_autorole(self, ctx: discord.Interaction, role: discord.Role):
        query = "INSERT INTO autorole VALUES (?, ?)"
        cursor.execute(query, (ctx.guild.id, role.id))
        database.commit()
        await ctx.response.send_message("Added an Autorole")


    @app_commands.command(name='remove_autorole', description="removes an autorole")
    @commands.has_permissions(manage_messages=True)
    async def remove_autorole(self, ctx: discord.Interaction, role: discord.Role):
        data_role = cursor.execute(f"SELECT * FROM autorole WHERE guild_id = {ctx.guild.id} AND role = {role.id}").fetchall()
        if not data_role:
            return await ctx.response.send_message("Autorole setting doesn't exists")
        cursor.execute(f"DELETE FROM autorole WHERE guild_id = {ctx.guild.id} AND role = {role.id}")
        database.commit()
        await ctx.response.send_message("removed the autoRole")
        
      

async def setup(client: commands.Bot) -> None:
    await client.add_cog(config(client))