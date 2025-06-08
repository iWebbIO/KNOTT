import discord
from discord.ext import commands
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class AchievementCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
    
    @commands.command()
    async def achievements(self, ctx, member: discord.Member = None):
        try:
            target = member or ctx.author
            guild_id = ctx.guild.id if ctx.guild else None
            
            user_achievements = await self.db_manager.get_user_achievements(target.id, guild_id)
            total_achievements = await self.db_manager.get_total_achievements()
            
            embed = discord.Embed(
                title=f"{target.display_name}'s Achievements",
                description=f"Unlocked {len(user_achievements)}/{total_achievements} achievements",
                color=discord.Color.gold()
            )
            
            if user_achievements:
                achievement_list = []
                for achievement in user_achievements[:10]:
                    name, description, earned_at = achievement
                    achievement_list.append(f"🏆 **{name}**\n{description}")
                
                embed.add_field(
                    name="Recent Achievements",
                    value="\n\n".join(achievement_list),
                    inline=False
                )
                
                if len(user_achievements) > 10:
                    embed.set_footer(text=f"Showing 10 of {len(user_achievements)} achievements")
            else:
                embed.add_field(
                    name="No Achievements Yet",
                    value="Start chatting to unlock your first achievement!",
                    inline=False
                )
            
            embed.set_thumbnail(url=target.display_avatar.url)
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in achievements command: {e}")
            await ctx.send("An error occurred while retrieving achievements.")
    
    @commands.command()
    async def achievementlist(self, ctx):
        try:
            all_achievements = await self.db_manager.get_all_achievements()
            
            embed = discord.Embed(
                title="Available Achievements",
                description=f"There are {len(all_achievements)} achievements to unlock!",
                color=discord.Color.blue()
            )
            
            level_achievements = []
            message_achievements = []
            special_achievements = []
            
            for achievement in all_achievements:
                name, description, req_type, req_value = achievement
                if req_type == "level":
                    level_achievements.append(f"**{name}** (Level {req_value})\n{description}")
                elif req_type == "messages":
                    message_achievements.append(f"**{name}** ({req_value} messages)\n{description}")
                else:
                    special_achievements.append(f"**{name}**\n{description}")
            
            if level_achievements:
                embed.add_field(
                    name="🎯 Level Achievements",
                    value="\n\n".join(level_achievements[:5]),
                    inline=False
                )
            
            if message_achievements:
                embed.add_field(
                    name="💬 Message Achievements",
                    value="\n\n".join(message_achievements[:5]),
                    inline=False
                )
            
            if special_achievements:
                embed.add_field(
                    name="⭐ Special Achievements",
                    value="\n\n".join(special_achievements[:5]),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in achievementlist command: {e}")
            await ctx.send("An error occurred while retrieving achievement list.")

async def setup(bot):
    await bot.add_cog(AchievementCommands(bot))
