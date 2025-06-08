import discord
from discord.ext import commands, tasks
import getrank
import asyncio
import time
import logging
from typing import Optional
import botsettings
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOTNAME = botsettings.name

db_manager = DatabaseManager()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix=botsettings.command_prefix, 
    intents=intents,
    help_command=None
)

user_cooldowns = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await db_manager.init_database()
    
    try:
        await bot.load_extension('commands.admin')
        print("Admin commands loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load admin commands: {e}")
    
    try:
        await bot.load_extension('commands.achievements')
        print("Achievement commands loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load achievement commands: {e}")
    
    try:
        await bot.load_extension('commands.roles')
        print("Role commands loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load role commands: {e}")
    
    try:
        await db_manager.initialize_default_achievements()
        print("Default achievements initialized")
    except Exception as e:
        logger.error(f"Failed to initialize achievements: {e}")
    
    update_presence.start()

@tasks.loop(minutes=5)
async def update_presence():
    server_count = len(bot.guilds)
    await bot.change_presence(activity=discord.Game(name=f'Say "kwhat" for help | {server_count} servers'))

@bot.command()
@commands.is_owner()
async def set(ctx, member: discord.Member, new_level: int):
    try:
        embed = discord.Embed(
            title="Level Set",
            description=f"Successfully set {member.mention}'s level to {new_level}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error in set command: {e}")
        await ctx.send("An error occurred while setting the level.")

@bot.command()
async def level(ctx):
    try:
        guild_id = ctx.guild.id if ctx.guild else None
        user_data = await db_manager.get_user_data(ctx.author.id, guild_id)
        
        if user_data:
            if guild_id:
                xp, level, total_messages = user_data
            else:
                xp, level, total_messages = user_data
            
            xp_needed = level * botsettings.level_up_base
            user_rank = getrank.get_rank(int(level))
            rank_position = await db_manager.get_user_rank(ctx.author.id, guild_id)
            
            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s Level",
                color=discord.Color.blue()
            )
            embed.add_field(name="Level", value=f"{level}", inline=True)
            embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
            embed.add_field(name="Rank", value=f"#{rank_position}", inline=True)
            embed.add_field(name="Title", value=user_rank, inline=False)
            embed.add_field(name="Messages Sent", value=f"{total_messages}", inline=True)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="No Data Found",
                description="You haven't sent any messages yet! Start chatting to gain XP.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error in level command: {e}")
        await ctx.send("An error occurred while retrieving your level data.")

@bot.command()
async def many(ctx):
    server_count = len(bot.guilds)
    
    embed = discord.Embed(
        title=f"{BOTNAME} Server Count",
        description=f"{BOTNAME} is running in **{server_count}** servers! 🚀",
        color=discord.Color.green()
    )
    
    if ctx.author.id == botsettings.owner_id:
        server_list = "\n".join([f"• {guild.name}" for guild in bot.guilds[:10]])
        if len(bot.guilds) > 10:
            server_list += f"\n... and {len(bot.guilds) - 10} more"
        embed.add_field(name="Servers", value=server_list, inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def what(ctx):
    embed = discord.Embed(
        title=f"{BOTNAME} Bot Commands",
        description="Here are all the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 Level Commands",
        value="• `klevel` - Check your XP and level\n• `kboard` - See the leaderboard\n• `krank` - Check your server rank",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Achievement Commands",
        value="• `kachievements` - View your achievements\n• `kachievementlist` - See all available achievements",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Info Commands", 
        value="• `kmany` - Check server count\n• `kwhat` - Show this help message",
        inline=False
    )
    
    if ctx.guild and ctx.author.guild_permissions.administrator:
        embed.add_field(
            name="⚙️ Server Admin Commands",
            value="• `ksetxp` - Set XP multiplier\n• `klevelchannel` - Set level up channel\n• `ktoggleannouncements` - Toggle announcements\n• `kserverconfig` - View server settings",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Rank Role Commands",
            value="• `kaddrankrole` - Add rank role for level\n• `kremoverankrole` - Remove rank role\n• `krankroles` - View configured roles\n• `ksyncranks` - Sync all user roles",
            inline=False
        )
    
    if ctx.author.id == botsettings.owner_id:
        embed.add_field(
            name="🔧 Owner Commands",
            value="• `kset` - Set user level (Owner only)",
            inline=False
        )
    
    embed.set_footer(text="Gain XP by chatting in servers!")
    await ctx.send(embed=embed)

@bot.command()
async def board(ctx):
    try:
        guild_id = ctx.guild.id if ctx.guild else None
        results = await db_manager.get_leaderboard(guild_id, limit=10)
        
        if not results:
            embed = discord.Embed(
                title="Leaderboard",
                description="No users found on the leaderboard yet!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"🏆 {'Server' if guild_id else 'Global'} Leaderboard",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        for index, result in enumerate(results, start=1):
            if guild_id:
                user_id, level, xp, total_messages = result
                xp_needed = level * botsettings.level_up_base
            else:
                user_id, total_xp, max_level, total_messages = result
                level = max_level
                xp = total_xp
                xp_needed = level * botsettings.level_up_base
            
            user = bot.get_user(user_id)
            if user:
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"{index}."
                leaderboard_text += f"{medal} **{user.display_name}** - Level {level} ({xp}/{xp_needed} XP)\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text=f"Showing top {len(results)} users")
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in board command: {e}")
        await ctx.send("An error occurred while retrieving the leaderboard.")

@bot.command()
async def rank(ctx, member: discord.Member = None):
    try:
        target = member or ctx.author
        guild_id = ctx.guild.id if ctx.guild else None
        
        user_data = await db_manager.get_user_data(target.id, guild_id)
        if not user_data:
            embed = discord.Embed(
                title="No Data Found",
                description=f"{target.display_name} hasn't sent any messages yet!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        rank_position = await db_manager.get_user_rank(target.id, guild_id)
        
        if guild_id:
            xp, level, total_messages = user_data
        else:
            xp, level, total_messages = user_data
        
        embed = discord.Embed(
            title=f"{target.display_name}'s Rank",
            description=f"Rank: **#{rank_position}** {'in this server' if guild_id else 'globally'}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="XP", value=f"{xp}/{level * botsettings.level_up_base}", inline=True)
        embed.add_field(name="Messages", value=total_messages, inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in rank command: {e}")
        await ctx.send("An error occurred while retrieving rank data.")

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith(bot.command_prefix):
            await bot.process_commands(message)
        return

    current_time = int(time.time())
    user_key = f"{message.author.id}_{message.guild.id}"
    
    if user_key in user_cooldowns:
        if current_time - user_cooldowns[user_key] < botsettings.xp_cooldown:
            await bot.process_commands(message)
            return
    
    user_cooldowns[user_key] = current_time
    
    try:
        guild_settings = await db_manager.get_guild_settings(message.guild.id)
        xp_multiplier = guild_settings[0] if guild_settings else 1.0
        
        xp_gain = int(botsettings.xp_per_message * xp_multiplier)
        
        new_xp, new_level, leveled_up = await db_manager.update_user_xp(
            message.author.id, 
            message.guild.id, 
            xp_gain, 
            current_time
        )
        
        user_data = await db_manager.get_user_data(message.author.id, message.guild.id)
        if user_data:
            _, current_level, total_messages = user_data
            earned_achievements = await db_manager.check_and_award_achievements(
                message.author.id, 
                message.guild.id, 
                current_level, 
                total_messages
            )
            
            for achievement_id, achievement_name, reward_xp in earned_achievements:
                achievement_embed = discord.Embed(
                    title="🏆 Achievement Unlocked!",
                    description=f"{message.author.mention} earned the **{achievement_name}** achievement!",
                    color=discord.Color.purple()
                )
                if reward_xp > 0:
                    achievement_embed.add_field(name="Bonus XP", value=f"+{reward_xp} XP", inline=True)
                achievement_embed.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(embed=achievement_embed)
        
        if leveled_up:
            user_rank = getrank.get_rank(new_level)
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} reached **Level {new_level}**!",
                color=discord.Color.gold()
            )
            embed.add_field(name="New Rank", value=user_rank, inline=False)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            try:
                rank_roles = await db_manager.get_rank_roles_for_level(message.guild.id, new_level)
                assigned_roles = []
                
                for role_id in rank_roles:
                    role = message.guild.get_role(role_id)
                    if role and role not in message.author.roles:
                        try:
                            await message.author.add_roles(role, reason=f"Reached level {new_level}")
                            assigned_roles.append(role.mention)
                        except discord.Forbidden:
                            logger.warning(f"Cannot assign role {role.name} to {message.author.display_name}")
                        except Exception as e:
                            logger.error(f"Error assigning role: {e}")
                
                if assigned_roles:
                    embed.add_field(
                        name="🎭 New Roles",
                        value="\n".join(assigned_roles),
                        inline=False
                    )
            except Exception as e:
                logger.error(f"Error processing rank roles: {e}")
            
            if guild_settings and guild_settings[1]:
                channel = bot.get_channel(guild_settings[1])
                if channel:
                    await channel.send(embed=embed)
                else:
                    await message.channel.send(embed=embed)
            else:
                await message.channel.send(embed=embed)
                
    except Exception as e:
        logger.error(f"Error processing XP gain: {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(botsettings.token)
