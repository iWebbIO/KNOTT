import discord
from discord.ext import commands
import botsettings
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setxp(self, ctx, xp_multiplier: float):
        try:
            # Check if user is bot owner or if this is a self-hosted instance
            if ctx.author.id != botsettings.owner_id and not botsettings.is_self_hosted:
                embed = discord.Embed(
                    title="Access Denied",
                    description="Only the bot owner can modify XP multipliers on hosted instances. If you're self-hosting, set `IS_SELF_HOSTED=True` in your environment variables.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            if xp_multiplier < 0.1 or xp_multiplier > 5.0:
                await ctx.send("XP multiplier must be between 0.1 and 5.0")
                return
            
            await self.db_manager.update_guild_settings(
                ctx.guild.id, 
                xp_multiplier=xp_multiplier
            )
            
            embed = discord.Embed(
                title="XP Multiplier Updated",
                description=f"XP multiplier set to **{xp_multiplier}x** for this server",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in setxp command: {e}")
            await ctx.send("An error occurred while updating XP multiplier.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def levelchannel(self, ctx, channel: discord.TextChannel = None):
        try:
            if channel is None:
                await self.db_manager.update_guild_settings(
                    ctx.guild.id,
                    level_up_channel=None
                )
                embed = discord.Embed(
                    title="Level Up Channel Removed",
                    description="Level up announcements will now appear in the same channel as the message",
                    color=discord.Color.orange()
                )
            else:
                await self.db_manager.update_guild_settings(
                    ctx.guild.id,
                    level_up_channel=channel.id
                )
                embed = discord.Embed(
                    title="Level Up Channel Set",
                    description=f"Level up announcements will now appear in {channel.mention}",
                    color=discord.Color.green()
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in levelchannel command: {e}")
            await ctx.send("An error occurred while setting the level up channel.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggleannouncements(self, ctx):
        try:
            guild_settings = await self.db_manager.get_guild_settings(ctx.guild.id)
            current_setting = guild_settings[2] if guild_settings else True
            
            new_setting = not current_setting
            await self.db_manager.update_guild_settings(
                ctx.guild.id,
                announcement_enabled=new_setting
            )
            
            status = "enabled" if new_setting else "disabled"
            embed = discord.Embed(
                title="Announcements Updated",
                description=f"Level up announcements are now **{status}**",
                color=discord.Color.green() if new_setting else discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in toggleannouncements command: {e}")
            await ctx.send("An error occurred while toggling announcements.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def serverconfig(self, ctx):
        try:
            guild_settings = await self.db_manager.get_guild_settings(ctx.guild.id)
            
            if guild_settings:
                xp_multiplier, level_up_channel_id, announcement_enabled, custom_prefix = guild_settings
            else:
                xp_multiplier = 1.0
                level_up_channel_id = None
                announcement_enabled = True
                custom_prefix = None
            
            embed = discord.Embed(
                title=f"Server Configuration - {ctx.guild.name}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="XP Multiplier", value=f"{xp_multiplier}x", inline=True)
            embed.add_field(name="Announcements", value="✅ Enabled" if announcement_enabled else "❌ Disabled", inline=True)
            embed.add_field(name="Prefix", value=custom_prefix or botsettings.command_prefix, inline=True)
            
            if level_up_channel_id:
                channel = self.bot.get_channel(level_up_channel_id)
                channel_name = channel.mention if channel else "Channel not found"
            else:
                channel_name = "Same as message channel"
            
            embed.add_field(name="Level Up Channel", value=channel_name, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in serverconfig command: {e}")
            await ctx.send("An error occurred while retrieving server configuration.")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
