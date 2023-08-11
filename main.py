import discord
from discord.ext import commands
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('Users.db')
cursor = conn.cursor()

# Create a table to store user information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        xp INTEGER,
        level INTEGER
    )
''')
conn.commit()

# Set up the bot
bot = commands.Bot(command_prefix='k', intents=discord.Intents().all())


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command()
async def level(ctx):
    # Retrieve user's XP and level from the database
    cursor.execute('SELECT xp, level FROM users WHERE user_id = ?',
                   (ctx.author.id, ))
    result = cursor.fetchone()
    if result:
        xp, level = result
        xpremaining = (level * 50)
        await ctx.reply(
            f'You are on level *{level}*! (Next level: {level+1})\nXP: {xp}/{xpremaining}'
        )
    else:
        await ctx.send(
            'Something went wrong. You can contact us in the support server.')


@bot.command()
async def many(ctx):
    if ctx.author.id == 697509268085145630:  # Replace with your user ID
        server_list = "\n".join([guild.name for guild in bot.guilds])
        await ctx.send(
            f"KnotT is running in {len(bot.guilds)} servers:\n{server_list}")
    else:
        await ctx.send(
            f"KnotT is running in {len(bot.guilds)} servers. Let's go!")


@bot.command()
async def what(ctx):
    # List out the available commands
    help_message = """
    KnotT Bot Commands:
    - klevel: Check your XP and level.
    - kmany: Check how many servers the bot is in.
    - kboard: See the leaderboard for the top 20 chatters.
    """
    await ctx.send(help_message)


@bot.command()
async def board(ctx):
    # Retrieve the top 20 chatters based on level and XP
    cursor.execute(
        'SELECT user_id, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT 20'
    )
    results = cursor.fetchall()

    leaderboard = ""
    for index, result in enumerate(results, start=1):
        user_id, level, xp = result
        user = bot.get_user(user_id)
        if user:
            leaderboard += f"{index}. {user.name} - Level: {level} - XP: {xp}\n"

    if leaderboard:
        await ctx.send("Top 20 Chatters:\n" + leaderboard)
    else:
        await ctx.send("No users found.")


@bot.event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Retrieve user's XP and level from the database
    cursor.execute('SELECT xp, level FROM users WHERE user_id = ?',
                   (message.author.id, ))
    result = cursor.fetchone()
    if result:
        xp, level = result
        xp += 1
        if xp >= level * 50:
            xp = 0
            level += 1
        cursor.execute('UPDATE users SET xp = ?, level = ? WHERE user_id = ?',
                       (xp, level, message.author.id))
    else:
        cursor.execute(
            'INSERT INTO users (user_id, xp, level) VALUES (?, 1, 1)',
            (message.author.id, ))
    conn.commit()

    await bot.process_commands(message)


# Run bot
bot.run("PLACE YOUR BOT TOKEN HERE")
