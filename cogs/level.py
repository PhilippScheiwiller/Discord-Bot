import discord
from discord import app_commands
from discord.ext import commands
import random
import sqlite3
from easy_pil import *

database = sqlite3.connect("config.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS leveling(guild_id INT, level INT, xp INT, user_id INT)")

class level(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        check = cursor.execute(f"SELECT * FROM levelSettings WHERE guild_id = {message.guild.id}").fetchall()
        if not check:
            return
        else:
            for var in check:
                enable_bool = var[1]
            if enable_bool == 0:
                return
        author = message.author
        guild = message.guild
        data = cursor.execute(f"SELECT * FROM leveling WHERE guild_id = {guild.id} AND user_id = {author.id}").fetchall()
        if not data:
            query = "INSERT INTO leveling VALUES (?, ?, ?, ?)"
            cursor.execute(query, (guild.id, 0, 0, author.id))
            database.commit()
        else:
            for var in data:
                level = var[1]
                xp = var[2]
            
            if level < 5:
                xp += random.randint(1, 5)
                query = "UPDATE leveling SET xp = ? WHERE guild_id = ? AND user_id = ?"
                cursor.execute(query, (xp, guild.id, author.id))
                database.commit()
            else:
                rand = random.randint(1, (level//2))
                if rand <= 2:
                    xp += random.randint(1, 15)
                    query = "UPDATE leveling SET xp = ? WHERE guild_id = ? AND user_id = ?"
                    cursor.execute(query, (xp, guild.id, author.id))
                    database.commit()
            if xp >= 100 * (level + 1):

                level += 1
                role = cursor.execute(f"SELECT role FROM levelrewards WHERE guild_id = {message.guild.id} AND level_req= {level}").fetchone()
                query = "UPDATE leveling SET level = ?, xp = ? WHERE guild_id = ? AND user_id = ?"
                cursor.execute(query, (level, 0, guild.id, author.id))
                database.commit()

                userData = {
                    "name": author.name,
                    "xp": xp,
                    "level": level,
                    "next_level_xp": 100 * (level + 1),
                    "percentage": 100 - ((100 * (level + 1) - xp) * 100) / (100 * (level + 1)),
                }


                background = Editor(Canvas((900, 300), color="#23272a"))
                background.rectangle((15, 15), width=870, height=270, color="#2b2f35",)

                arrow = Editor("image/Arrow.png").resize((100, 100))

                poppins = Font.poppins(size=40, variant="bold")
                poppins_small = Font.poppins(size=30, variant="bold" )

                card_right_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]
                background.polygon(card_right_shape, color="#FFFFFF")

                background.text((50, 70), userData["name"], font=poppins, color="#FFFFFF")
                background.rectangle((50, 120), width=400, height=6, fill="#FFFFFF", radius=4)

                background.rectangle((50, 150), width=100, height=100, color="#FFFFFF", radius=20)
                background.rectangle((60, 160), width=80, height=80, color="#2b2f35", radius=15)
                background.text((100, 185), str(level-1), font=poppins, align= "center", color="#FFFFFF")

                background.paste(arrow, (200, 150))

                background.rectangle((350, 150), width=100, height=100, color="#FFFFFF", radius=20)
                background.rectangle((360, 160), width=80, height=80, color="#2b2f35", radius=15)
                background.text((400, 185), str(level), font=poppins, align= "center", color="#FFFFFF")
                background.text((475, 185), "Level up! ", font=poppins_small, color="#FFFFFF")

                file = discord.File(fp=background.image_bytes, filename="Levelcard.png")

                if role:
                    role = role[0]
                    role = guild.get_role(role)
                    try:
                        await author.add_roles(role)
                        await message.channel.send(f"{author.mention} has leveled up to level **{level}** and received the **{role.name}** role", file=file)
                    except discord.HTTPException:
                        await message.channel.send(f"{author.mention} has leveled up to level **{level}**! | WASN't ABLE TO GIVE LEVEL ROLE", file=file)
                else:
                    await message.channel.send(file=file)


    @app_commands.command(name='level', description="Show a your or another members level")
    async def level(self, ctx: discord.Interaction, member: discord.Member = None):
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
        if member == self.client.user:
            await ctx.response.send_message("The bot doesn't have a level", ephemeral=True)
            return
        if member is None:
            member = ctx.user

        data = cursor.execute(f"SELECT * FROM leveling WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}").fetchall()
        if not data:
            query = "INSERT INTO leveling VALUES (?, ?, ?, ?)"
            cursor.execute(query, (ctx.guild.id, 0, 0, member.id))
            database.commit()
            xp = 0
            level = 0
        else:
            for var in data:
                level = var[1]
                xp = var[2]

        userData = {
            "name": member.name,
            "xp": xp,
            "level": level,
            "next_level_xp": 100 * (level + 1),
            "percentage": 100 - ((100 * (level + 1) - xp) * 100) / (100 * (level + 1)),
        }
        #percent = str(round(userData['percentage'], 0))+"%"

        background = Editor(Canvas((900, 300), color="#23272a"))
        background.rectangle((15, 15), width=870, height=270, color="#2b2f35",)
        profile_picture = await load_image_async(str(member.avatar.url))
        profile = Editor(profile_picture).resize((150, 150)).circle_image()
        background.rectangle((22, 22), width=165, height=165, color="#FFFFFF", radius=85)

        poppins = Font.poppins(size=40, variant="bold")
        poppins_small = Font.poppins(size=30, variant="bold" )

        card_right_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]
        background.polygon(card_right_shape, color="#FFFFFF")
        background.paste(profile, (30, 30))

        background.rectangle((30, 220), width=650, height=40, color="#282828", radius=20)
        if userData['percentage'] >= 5:
            background.bar((30, 220), max_width=650, height=40, percentage=userData["percentage"], color="#167ac5", radius=20)
        elif userData['percentage'] < 5 and userData['percentage'] > 0:
            background.bar((30, 220), max_width=650, height=40, percentage=5, color="#167ac5", radius=20)
        background.text((200, 40), userData["name"], font=poppins, color="#FFFFFF")
        background.rectangle((200, 100), width=350, height=6, fill="#FFFFFF", radius=4)
        background.text((200, 130), f"Level - {userData['level']} | XP - {userData['xp']}/{userData['next_level_xp']}", font=poppins_small, color="#FFFFFF")

        file = discord.File(fp=background.image_bytes, filename="rankcard.png")
        await ctx.response.send_message(file=file)

    @app_commands.command(name='leaderboard', description="Shows the Leaderboard")
    async def leaderboard(self, ctx: discord.Interaction):
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
        data = cursor.execute(f"SELECT * FROM leveling WHERE guild_id = {ctx.guild.id} ORDER BY level DESC, xp DESC LIMIT 10").fetchall()
        if not data:
            ctx.response.send_message("No data for this guild found", ephemeral=True)
        elif data:
            em = discord.Embed(title="Leaderboard")
            count = 0
            for var in data:
                count += 1
                user = ctx.guild.get_member(var[3])
                em.add_field(name=f"{count}. {user.name}", value=f"Level-**{var[1]}** | xp-**{var[2]}**", inline=False)
            await ctx.response.send_message(embed=em)

    @app_commands.command(name='lvlrewards', description="Shows the rewards for leveling")
    async def lvlrewards(self, ctx: discord.Interaction):
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
        data = cursor.execute(f"SELECT * FROM levelrewards WHERE guild_id = {ctx.guild.id} ORDER BY level_req ASC").fetchall()
        if not data:
            return await ctx.response.send_message("No role levels have been setup for this guild!")
        em = discord.Embed(title="role levels", description="role levels for this guild")
        for var in data:
            em.add_field(name=f"level-{var[2]}", value=f"{ctx.guild.get_role(var[1]).mention}", inline=False)
        await ctx.response.send_message(embed=em)



async def setup(client: commands.Bot) -> None:
    await client.add_cog(level(client))
