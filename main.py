
import os
from keep_alive import keep_alive
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="kn ")


@bot.event
async def on_ready():
    print("Logged in to Knott-BOT")
    print(bot.user)

@bot.event
async def on_guild_join(guild):
	status = discord.game(name=f"On {len(bot.guilds)}", type=3)
	await bot.change_presence(discord.status.online, status=status)
	


keep_alive()
bot.run(os.environ.get("BOT_TKN"))
